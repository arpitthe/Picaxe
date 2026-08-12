import { Injectable, Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../database/prisma.service';
import { ConfigService } from '@nestjs/config';
import { BusinessValidationException } from '../shared/exceptions';
import { JwtPayload } from '../shared/types';
import * as bcrypt from 'bcrypt';
import { RegisterDto, LoginDto } from './dto/auth.dto';

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
    private configService: ConfigService,
  ) {}

  async register(dto: RegisterDto) {
    const existingUser = await this.prisma.user.findFirst({
      where: { credentials: { some: { email: dto.email } } },
    });
    if (existingUser) {
      throw new BusinessValidationException('Email already in use');
    }

    const hashedPassword = await bcrypt.hash(dto.password, 10);
    
    // Create User, UserCredential, and StudentProfile in a transaction
    const user = await this.prisma.user.create({
      data: {
        displayName: dto.name,
        role: 'STUDENT',
        credentials: {
          create: {
            provider: 'EMAIL',
            providerId: dto.email,
            email: dto.email,
            passwordHash: hashedPassword,
          }
        },
        studentProfile: {
          create: {
            fullName: dto.name,
            institution: dto.institution,
          }
        }
      },
    });

    this.logger.log(`Registered new student user: ${user.id}`);
    return this.generateTokens(user.id, user.role);
  }

  async login(dto: LoginDto) {
    const creds = await this.prisma.userCredential.findFirst({
      where: { email: dto.email, provider: 'EMAIL' },
      include: { user: true },
    });

    if (!creds || !creds.passwordHash) {
      throw new BusinessValidationException('Invalid email or password');
    }

    const isMatch = await bcrypt.compare(dto.password, creds.passwordHash);
    if (!isMatch) {
      throw new BusinessValidationException('Invalid email or password');
    }

    await this.prisma.user.update({
      where: { id: creds.userId },
      data: { lastLoginAt: new Date() },
    });

    this.logger.log(`User logged in: ${creds.userId}`);
    return this.generateTokens(creds.userId, creds.user.role);
  }

  private async generateTokens(userId: string, role: string) {
    const payload: JwtPayload = { sub: userId, role };
    const accessToken = this.jwtService.sign(payload);
    
    // Generate refresh token logic would go here
    return {
      accessToken,
      // refreshToken: ...,
      user: { id: userId, role }
    };
  }
}
