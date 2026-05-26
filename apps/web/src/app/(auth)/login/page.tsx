'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { Loader2, Lock, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { z } from 'zod';

import { BrandMark } from '@/components/layout/brand';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { authApi } from '@/lib/api/endpoints';
import { APP_TAGLINE, ROUTES } from '@/lib/constants';
import { useAuthStore } from '@/stores/auth-store';

const schema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Min 8 characters'),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      const res = await authApi.login({
        email: values.email,
        password: values.password,
      });
      setAuth(res);
      toast.success(`Welcome, ${res.user.full_name}`);
      router.replace(ROUTES.dashboard);
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message ?? 'Authentication failed');
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left — brand panel */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-gradient-to-br from-ivory-100 via-ivory-50 to-accent-50 relative overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-accent-100 blur-3xl opacity-60" />
        <div className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-accent-50 blur-3xl opacity-80" />

        <BrandMark />

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 max-w-md"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/70 border border-accent-100 text-accent-700 text-xs font-medium mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            Azure OpenAI GPT-5
          </div>
          <h1 className="font-serif text-4xl xl:text-5xl text-ink-900 text-balance leading-tight">
            Turn transcripts into <em className="text-accent-600 not-italic">audit-ready SOPs</em>.
          </h1>
          <p className="mt-5 text-ink-600 text-lg leading-relaxed">
            {APP_TAGLINE}. Upload KT sessions, meeting transcripts, or walk-throughs — TranscribeOP
            produces structured Standard Operating Procedures in seconds.
          </p>
        </motion.div>

        <div className="relative z-10 text-xs text-ink-500">© 2026 TranscribeOP · Enterprise</div>
      </div>

      {/* Right — form */}
      <div className="flex items-center justify-center p-6 sm:p-12">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-sm space-y-8"
        >
          <div className="lg:hidden">
            <BrandMark />
          </div>

          <div>
            <h2 className="font-serif text-3xl text-ink-900">Sign in</h2>
            <p className="text-ink-600 mt-1 text-sm">
              Authorized personnel only. Use your provisioned portal credentials.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-ink-700">Email</label>
              <Input
                type="email"
                placeholder="you@company.com"
                autoComplete="username"
                {...register('email')}
              />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-ink-700">Password</label>
              <Input
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" size="lg" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Sign in
            </Button>
          </form>

          <div className="flex items-center justify-center gap-1.5 text-xs text-ink-500">
            <Lock className="h-3 w-3" />
            <span>Restricted portal · access by invitation only</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
