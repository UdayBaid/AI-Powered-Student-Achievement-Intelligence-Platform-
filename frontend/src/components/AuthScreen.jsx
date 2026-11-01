import { useState } from 'react'
import {
  ArrowRight,
  GraduationCap,
  LockKeyhole,
  Mail,
  UserRound,
} from 'lucide-react'

function AuthScreen({ mode, resetToken, onModeChange, onSubmit, loading, error, notice }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const isRegister = mode === 'register'
  const isForgot = mode === 'forgot'
  const isReset = mode === 'reset'
  const isLogin = mode === 'login'
  const isPasswordForm = isLogin || isRegister || isReset

  const submit = event => {
    event.preventDefault()
    if ((isRegister || isReset) && password !== confirmPassword) {
      onSubmit({ validationError: 'Passwords do not match.' })
      return
    }
    onSubmit({ name: name.trim(), email: email.trim(), password, token: resetToken })
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-8">
      <div className="mx-auto grid min-h-[min(760px,calc(100vh-4rem))] max-w-5xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm md:grid-cols-[0.9fr_1.1fr]">
        <section className="flex flex-col justify-between bg-blue-700 p-7 text-white sm:p-10">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-white/15 p-2.5"><GraduationCap size={25} /></span>
            <div>
              <p className="text-lg font-bold">StudentAI</p>
              <p className="text-xs text-blue-100">Achievement Platform</p>
            </div>
          </div>
          <div className="py-8">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-100">Student intelligence</p>
            <h1 className="mt-3 max-w-sm text-3xl font-semibold leading-tight sm:text-4xl">
              Your academic journey, understood.
            </h1>
            <p className="mt-4 max-w-sm text-sm leading-6 text-blue-100">
              Sign in to view your dashboard and request a personalized grade estimate.
            </p>
          </div>
          <p className="text-xs text-blue-100">Private account access</p>
        </section>

        <section className="flex items-center justify-center p-6 sm:p-10">
          <div className="w-full max-w-md">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-900">
                {isRegister ? 'Create your account' : isForgot ? 'Reset your password' : isReset ? 'Choose a new password' : 'Welcome back'}
              </h2>
              <p className="mt-2 text-sm text-slate-500">
                {isRegister
                  ? 'Use your email to set up StudentAI.'
                  : isForgot
                    ? 'We’ll email a one-time reset link if an account matches.'
                    : isReset
                      ? 'Choose a new password for your account.'
                      : 'Sign in to continue to your dashboard.'}
              </p>
            </div>

            {(isLogin || isRegister) ? (
              <div className="mb-6 grid grid-cols-2 rounded-lg bg-slate-100 p-1" role="tablist" aria-label="Authentication">
                <button
                  type="button"
                  role="tab"
                  aria-selected={isLogin}
                  onClick={() => onModeChange('login')}
                  className={`rounded-md px-3 py-2.5 text-sm font-semibold ${isLogin ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-500'}`}
                >
                  Sign in
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={isRegister}
                  onClick={() => onModeChange('register')}
                  className={`rounded-md px-3 py-2.5 text-sm font-semibold ${isRegister ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-500'}`}
                >
                  Create account
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => onModeChange('login')}
                className="mb-6 text-sm font-semibold text-blue-700 hover:text-blue-800"
              >
                Back to sign in
              </button>
            )}

            {notice && <p className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800" role="status">{notice}</p>}
            {error && <p className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p>}

            <form className="space-y-4" onSubmit={submit}>
              {!isReset && (
                <label className="block">
                  <span className="mb-1.5 block text-sm font-medium text-slate-700">Email</span>
                  <span className="relative block">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
                    <input
                      type="email"
                      autoComplete="email"
                      required
                      maxLength={254}
                      value={email}
                      onChange={event => setEmail(event.target.value)}
                      className="w-full rounded-lg border border-slate-200 py-3 pl-10 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                      placeholder="you@example.com"
                    />
                  </span>
                </label>
              )}

              {isRegister && (
                <label className="block">
                  <span className="mb-1.5 block text-sm font-medium text-slate-700">Name</span>
                  <span className="relative block">
                    <UserRound className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
                    <input
                      autoComplete="name"
                      required
                      maxLength={100}
                      value={name}
                      onChange={event => setName(event.target.value)}
                      className="w-full rounded-lg border border-slate-200 py-3 pl-10 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                      placeholder="Your name"
                    />
                  </span>
                </label>
              )}

              {isPasswordForm && <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-slate-700">Password</span>
                <span className="relative block">
                  <LockKeyhole className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
                  <input
                    type="password"
                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                    required
                    minLength={isLogin ? 1 : 12}
                    maxLength={128}
                    value={password}
                    onChange={event => setPassword(event.target.value)}
                    className="w-full rounded-lg border border-slate-200 py-3 pl-10 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    placeholder={isLogin ? 'Your password' : 'At least 12 characters'}
                  />
                </span>
              </label>}

              {(isRegister || isReset) && (
                <label className="block">
                  <span className="mb-1.5 block text-sm font-medium text-slate-700">Confirm password</span>
                  <span className="relative block">
                    <LockKeyhole className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
                    <input
                      type="password"
                      autoComplete="new-password"
                      required
                      minLength={12}
                      maxLength={128}
                      value={confirmPassword}
                      onChange={event => setConfirmPassword(event.target.value)}
                      className="w-full rounded-lg border border-slate-200 py-3 pl-10 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                      placeholder="Re-enter your password"
                    />
                  </span>
                </label>
              )}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-wait disabled:opacity-60"
              >
                {loading
                  ? 'Please wait…'
                  : isRegister
                    ? 'Create account'
                    : isForgot
                      ? 'Send reset link'
                      : isReset
                        ? 'Reset password'
                        : 'Sign in'}
                {!loading && <ArrowRight size={17} />}
              </button>
            </form>

            {isLogin && (
              <button
                type="button"
                onClick={() => onModeChange('forgot')}
                className="mt-4 text-sm font-medium text-blue-700 hover:text-blue-800"
              >
                Forgot password?
              </button>
            )}
            {isRegister && <p className="mt-4 text-xs leading-5 text-slate-500">Password must be at least 12 characters.</p>}
            {isReset && <p className="mt-4 text-xs leading-5 text-slate-500">Reset links expire after 15 minutes and can only be used once.</p>}
          </div>
        </section>
      </div>
    </main>
  )
}

export default AuthScreen
