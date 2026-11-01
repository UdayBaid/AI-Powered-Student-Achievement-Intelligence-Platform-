
import { useEffect, useState } from 'react'
import {
  GraduationCap, LayoutDashboard, BrainCircuit,
  ClipboardList, Lightbulb, ArrowLeft, ArrowRight,
  LoaderCircle, CheckCircle2, LogOut
} from 'lucide-react'
import AuthScreen from './components/AuthScreen.jsx'
import { apiRequest } from './api.js'

const sections = [
  {
    title: 'Personal Information',
    description: 'Basic details about the student.',
    fields: [
      { name: 'school', label: 'School', type: 'select', options: ['GP', 'MS'] },
      { name: 'sex', label: 'Gender', type: 'select', options: ['F', 'M'] },
      { name: 'age', label: 'Age', type: 'number', min: 15, max: 22 },
      { name: 'address', label: 'Address Type', type: 'select', options: ['U', 'R'], labels: ['Urban', 'Rural'] },
      { name: 'famsize', label: 'Family Size', type: 'select', options: ['GT3', 'LE3'], labels: ['More than 3', '3 or less'] },
      { name: 'Pstatus', label: 'Parents Living Together', type: 'select', options: ['T', 'A'], labels: ['Together', 'Apart'] },
    ],
  },
  {
    title: 'Family & Education',
    description: 'Family background and educational support.',
    fields: [
      { name: 'Medu', label: "Mother's Education", type: 'number', min: 0, max: 4, hint: '0: None, 1: Primary, 2: 5th–9th, 3: Secondary, 4: Higher' },
      { name: 'Fedu', label: "Father's Education", type: 'number', min: 0, max: 4, hint: '0: None, 1: Primary, 2: 5th–9th, 3: Secondary, 4: Higher' },
      { name: 'Mjob', label: "Mother's Job", type: 'select', options: ['teacher', 'health', 'services', 'at_home', 'other'] },
      { name: 'Fjob', label: "Father's Job", type: 'select', options: ['teacher', 'health', 'services', 'at_home', 'other'] },
      { name: 'reason', label: 'Reason for Choosing School', type: 'select', options: ['home', 'reputation', 'course', 'other'] },
      { name: 'guardian', label: 'Guardian', type: 'select', options: ['mother', 'father', 'other'] },
      { name: 'schoolsup', label: 'School Support', type: 'select', options: ['yes', 'no'] },
      { name: 'famsup', label: 'Family Educational Support', type: 'select', options: ['yes', 'no'] },
    ],
  },
  {
    title: 'Study Habits',
    description: 'Information about study routines and academic activities.',
    fields: [
      { name: 'traveltime', label: 'Travel Time to School', type: 'number', min: 1, max: 4, hint: '1: Under 15 min, 2: 15–30 min, 3: 30–60 min, 4: Over 60 min' },
      { name: 'studytime', label: 'Weekly Study Time', type: 'number', min: 1, max: 4, hint: '1: Under 2 hrs, 2: 2–5 hrs, 3: 5–10 hrs, 4: Over 10 hrs' },
      { name: 'failures', label: 'Past Class Failures', type: 'number', min: 0, max: 4 },
      { name: 'paid', label: 'Extra Paid Classes', type: 'select', options: ['yes', 'no'] },
      { name: 'activities', label: 'Extracurricular Activities', type: 'select', options: ['yes', 'no'] },
      { name: 'nursery', label: 'Attended Nursery School', type: 'select', options: ['yes', 'no'] },
      { name: 'higher', label: 'Wants Higher Education', type: 'select', options: ['yes', 'no'] },
      { name: 'internet', label: 'Internet Access at Home', type: 'select', options: ['yes', 'no'] },
    ],
  },
  {
    title: 'Lifestyle & Attendance',
    description: 'Daily habits, relationships and attendance.',
    fields: [
      { name: 'romantic', label: 'In a Romantic Relationship', type: 'select', options: ['yes', 'no'] },
      { name: 'famrel', label: 'Family Relationship Quality', type: 'number', min: 1, max: 5 },
      { name: 'freetime', label: 'Free Time After School', type: 'number', min: 1, max: 5 },
      { name: 'goout', label: 'Going Out with Friends', type: 'number', min: 1, max: 5 },
      { name: 'Dalc', label: 'Workday Alcohol Consumption', type: 'number', min: 1, max: 5 },
      { name: 'Walc', label: 'Weekend Alcohol Consumption', type: 'number', min: 1, max: 5 },
      { name: 'health', label: 'Current Health Status', type: 'number', min: 1, max: 5 },
      { name: 'absences', label: 'Number of School Absences', type: 'number', min: 0 },
    ],
  },
]

const emptyForm = Object.fromEntries(
  sections.flatMap(section => section.fields.map(field => [field.name, '']))
)

function App() {
  const [page, setPage] = useState('Dashboard')
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(emptyForm)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [selectedPrediction, setSelectedPrediction] = useState(null)
  const [historyError, setHistoryError] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resetToken, setResetToken] = useState(() => new URLSearchParams(window.location.search).get('reset_token') || '')
  const [token, setToken] = useState(() => resetToken ? '' : sessionStorage.getItem('studentai_access_token') || '')
  const [user, setUser] = useState(null)
  const [authChecking, setAuthChecking] = useState(() => Boolean(sessionStorage.getItem('studentai_access_token')) && !resetToken)
  const [authMode, setAuthMode] = useState(() => resetToken ? 'reset' : 'login')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState('')
  const [authNotice, setAuthNotice] = useState('')
  const displayedResult = selectedPrediction?.result || result || history[0]?.result || null
  const featureContributions = Array.isArray(displayedResult?.explanations)
    ? displayedResult.explanations
    : displayedResult?.explanations?.top_features || []
  const maxContribution = Math.max(
    0,
    ...featureContributions.map(item => Math.abs(item.contribution)),
  )

  useEffect(() => {
    let active = true

    if (!token) {
      return () => { active = false }
    }

    apiRequest('/auth/me', { token })
      .then(async authenticatedUser => {
        if (active) setUser(authenticatedUser)
        try {
          const records = await apiRequest('/predictions', { token })
          if (active) {
            setHistory(records)
            setHistoryError('')
          }
        } catch (historyRequestError) {
          if (!active) return
          if (historyRequestError.status === 401) {
            sessionStorage.removeItem('studentai_access_token')
            setToken('')
            setUser(null)
            setHistory([])
            setAuthMode('login')
            setAuthNotice('Your session expired. Please sign in again.')
          } else {
            setHistoryError(historyRequestError.message || 'Could not load saved predictions.')
          }
        }
      })
      .catch(requestError => {
        if (!active) return
        sessionStorage.removeItem('studentai_access_token')
        setToken('')
        setUser(null)
        setHistory([])
        setAuthMode('login')
        setAuthNotice(requestError.status === 401
          ? 'Your session expired. Please sign in again.'
          : requestError.message)
      })
      .finally(() => {
        if (active) setAuthChecking(false)
      })

    return () => { active = false }
  }, [token])

  const logout = (notice = '') => {
    sessionStorage.removeItem('studentai_access_token')
    setToken('')
    setUser(null)
    setResult(null)
    setHistory([])
    setSelectedPrediction(null)
    setHistoryError('')
    setPage('Dashboard')
    setStep(0)
    setAuthMode('login')
    setAuthNotice(notice)
    setAuthError('')
  }

  const authenticate = async values => {
    if (values.validationError) {
      setAuthError(values.validationError)
      return
    }

    setAuthError('')
    setAuthLoading(true)
    try {
      if (authMode === 'forgot') {
        const response = await apiRequest('/auth/forgot-password', {
          method: 'POST',
          body: { email: values.email },
        })
        setAuthMode('login')
        setAuthNotice(response.message)
        return
      }

      if (authMode === 'reset') {
        const response = await apiRequest('/auth/reset-password', {
          method: 'POST',
          body: { token: values.token, password: values.password },
        })
        sessionStorage.removeItem('studentai_access_token')
        setToken('')
        setUser(null)
        window.history.replaceState({}, '', window.location.pathname)
        setResetToken('')
        setAuthMode('login')
        setAuthNotice(response.message)
        return
      }

      if (authMode === 'register') {
        await apiRequest('/auth/register', {
          method: 'POST',
          body: { name: values.name, email: values.email, password: values.password },
        })
      }

      const session = await apiRequest('/auth/login', {
        method: 'POST',
        body: { email: values.email, password: values.password },
      })
      sessionStorage.setItem('studentai_access_token', session.access_token)
      setUser(session.user)
      setToken(session.access_token)
      setHistory([])
      setSelectedPrediction(null)
      setAuthNotice('')
      setAuthError('')
      setPage('Dashboard')
    } catch (requestError) {
      setAuthError(requestError.message || 'Authentication failed.')
    } finally {
      setAuthLoading(false)
    }
  }

  const updateField = (name, value) => {
    setForm(previous => ({ ...previous, [name]: value }))
  }

  const predict = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    const payload = Object.fromEntries(
      Object.entries(form).map(([key, value]) => [
        key,
        ['age', 'Medu', 'Fedu', 'traveltime', 'studytime',
          'failures', 'famrel', 'freetime', 'goout',
          'Dalc', 'Walc', 'health', 'absences'].includes(key)
          ? Number(value)
          : value
      ])
    )

    try {
      const data = await apiRequest('/predict', {
        method: 'POST',
        token,
        body: payload,
      })

      setResult(data)
      setSelectedPrediction(null)
      try {
        setHistory(await apiRequest('/predictions', { token }))
        setHistoryError('')
      } catch (historyRequestError) {
        setHistoryError(historyRequestError.message || 'Prediction saved, but history could not be refreshed.')
      }
      setPage('My Results')
    } catch (err) {
      if (err.status === 401) {
        logout('Your session expired. Please sign in again.')
        return
      }
      setError(err.message || 'Could not connect to the backend.')
    } finally {
      setLoading(false)
    }
  }

  const startPrediction = () => {
    setResult(null)
    setError('')
    setStep(0)
    setPage('Predict Grade')
  }

  if (authChecking) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-500">
        <LoaderCircle className="mr-2 animate-spin" size={18} /> Checking your session…
      </div>
    )
  }

  if (!token || !user) {
    return (
      <AuthScreen
        mode={authMode}
        resetToken={resetToken}
        onModeChange={mode => {
          if (mode === 'login' && resetToken) {
            window.history.replaceState({}, '', window.location.pathname)
            setResetToken('')
          }
          setAuthMode(mode)
          setAuthError('')
        }}
        onSubmit={authenticate}
        loading={authLoading}
        error={authError}
        notice={authNotice}
      />
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 md:flex">
      <aside className="w-full border-b border-slate-200 bg-white p-5 md:min-h-screen md:w-60 md:border-b-0 md:border-r">
        <div className="mb-7 flex items-center gap-3">
          <div className="rounded-xl bg-blue-600 p-2 text-white">
            <GraduationCap size={24} />
          </div>
          <div>
            <h1 className="font-bold text-slate-900">StudentAI</h1>
            <p className="text-xs text-slate-500">Achievement Platform</p>
          </div>
        </div>

        <nav className="flex gap-2 overflow-x-auto md:flex-col">
          {[
            ['Dashboard', LayoutDashboard],
            ['Predict Grade', BrainCircuit],
            ['My Results', ClipboardList],
            ['Recommendations', Lightbulb],
          ].map(([name, Icon]) => (
            <button
              key={name}
              onClick={() => setPage(name)}
              className={`flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium ${
                page === name ? 'bg-blue-50 text-blue-700' : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              <Icon size={18} />
              {name}
            </button>
          ))}
        </nav>
      </aside>

      <main className="min-w-0 flex-1">
        <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-5 py-5 sm:px-8">
          <div>
            <h2 className="font-bold text-slate-900">{page}</h2>
            <p className="text-xs text-slate-500">Student Achievement Intelligence Platform</p>
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <span className="hidden text-sm font-medium text-slate-700 sm:inline">{user.name}</span>
            <button
              type="button"
              onClick={() => logout()}
              title="Sign out"
              aria-label="Sign out"
              className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              <LogOut size={16} /><span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </header>

        <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
          {page === 'Dashboard' && (
            <>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Welcome, {user.name}!</h1>
                <p className="mt-2 text-sm text-slate-500">
                  Understand your academic performance with machine learning.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <Stat title="Predicted Grade" value={result ? `${Number(result.predicted_g3).toFixed(2)} / 20` : '-- / 20'} />
                <Stat title="Academic Assessment" value={result ? 'Completed' : 'Not assessed'} />
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-7">
                <BrainCircuit size={30} className="text-blue-600" />
                <h3 className="mt-4 text-lg font-bold">Predict your academic performance</h3>
                <p className="mt-2 text-sm text-slate-500">
                  Enter your academic, family and lifestyle details to get an estimated final grade.
                </p>
                <button onClick={startPrediction} className="mt-5 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700">
                  Start Prediction <ArrowRight className="ml-2 inline" size={17} />
                </button>
              </div>
            </>
          )}

          {page === 'Predict Grade' && (
            <form onSubmit={event => {
              if (step < sections.length - 1) {
                event.preventDefault()
                setStep(step + 1)
                setError('')
              } else {
                predict(event)
              }
            }} className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-8">

              <div className="mb-7">
                <p className="text-sm font-semibold text-blue-600">STEP {step + 1} OF {sections.length}</p>
                <h1 className="mt-2 text-xl font-bold text-slate-900">{sections[step].title}</h1>
                <p className="mt-1 text-sm text-slate-500">{sections[step].description}</p>
              </div>

              <div className="mb-8 flex gap-2">
                {sections.map((section, index) => (
                  <div key={section.title} className={`h-2 flex-1 rounded-full ${index <= step ? 'bg-blue-600' : 'bg-slate-100'}`} />
                ))}
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                {sections[step].fields.map(field => (
                  <label key={field.name} className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">{field.label}</span>

                    {field.type === 'select' ? (
                      <select
                        required
                        value={form[field.name]}
                        onChange={event => updateField(field.name, event.target.value)}
                        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500"
                      >
                        <option value="">Select an option</option>
                        {field.options.map((option, index) => (
                          <option key={option} value={option}>
                            {field.labels?.[index] || option}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        required
                        type="number"
                        min={field.min}
                        max={field.max}
                        step="1"
                        value={form[field.name]}
                        onChange={event => updateField(field.name, event.target.value)}
                        className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
                      />
                    )}

                    {field.hint && <span className="mt-1 block text-xs text-slate-400">{field.hint}</span>}
                  </label>
                ))}
              </div>

              {error && (
                <p className="mt-5 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>
              )}

              <div className="mt-9 flex justify-between gap-3">
                <button
                  type="button"
                  disabled={step === 0 || loading}
                  onClick={() => setStep(step - 1)}
                  className="flex items-center gap-2 rounded-xl border border-slate-200 px-5 py-3 text-sm font-medium disabled:opacity-40"
                >
                  <ArrowLeft size={17} /> Back
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                >
                  {loading ? <LoaderCircle className="animate-spin" size={17} /> : null}
                  {loading ? 'Predicting...' : step === sections.length - 1 ? 'Generate Prediction' : 'Continue'}
                  {!loading && <ArrowRight size={17} />}
                </button>
              </div>
            </form>
          )}

          {page === 'My Results' && (
            displayedResult ? (
              <div className="space-y-5">
                {historyError && (
                  <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800" role="status">
                    {historyError}
                  </p>
                )}

                {history.length > 0 && (
                  <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
                    <div className="mb-4 flex items-baseline justify-between gap-3">
                      <h3 className="font-bold text-slate-900">Saved predictions</h3>
                      <span className="text-xs text-slate-500">{history.length} shown</span>
                    </div>
                    <ul className="divide-y divide-slate-100">
                      {history.map(record => {
                        const isSelected = selectedPrediction?.id === record.id
                        return (
                          <li key={record.id}>
                            <button
                              type="button"
                              aria-pressed={isSelected}
                              onClick={() => {
                                setSelectedPrediction(record)
                                setResult(null)
                              }}
                              className={`flex w-full items-center justify-between gap-4 py-3 text-left ${isSelected ? 'text-blue-700' : 'text-slate-700 hover:text-blue-700'}`}
                            >
                              <span className="min-w-0">
                                <span className="block truncate text-sm font-semibold">
                                  Grade {Number(record.result.predicted_g3).toFixed(2)} / 20
                                </span>
                                <span className="mt-0.5 block text-xs text-slate-500">
                                  {new Date(record.created_at).toLocaleString()}
                                </span>
                              </span>
                              <ArrowRight className="shrink-0" size={17} />
                            </button>
                          </li>
                        )
                      })}
                    </ul>
                  </section>
                )}

                <div className="rounded-2xl border border-slate-200 bg-white p-7">
                  <CheckCircle2 className="text-green-600" size={28} />
                  <p className="mt-4 text-sm text-slate-500">Predicted Final Grade</p>
                  <h1 className="mt-1 text-4xl font-bold text-blue-700">
                    {Number(displayedResult.predicted_g3).toFixed(2)} <span className="text-lg text-slate-400">/ 20</span>
                  </h1>
                  <p className="mt-4 text-sm leading-6 text-slate-600">{displayedResult.interpretation}</p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-6">
                  <h3 className="font-bold">Personalized Recommendations</h3>
                  <ul className="mt-4 space-y-3">
                    {displayedResult.recommendations?.map((item, index) => (
                      <li key={index} className="flex gap-3 text-sm text-slate-600">
                        <CheckCircle2 size={18} className="shrink-0 text-green-600" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                {featureContributions.length > 0 && (
                  <div className="rounded-2xl border border-slate-200 bg-white p-6">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <h3 className="font-bold">What influenced this estimate?</h3>
                      {displayedResult.explanations?.baseline_prediction !== undefined && (
                        <span className="text-xs text-slate-500">
                          Baseline {Number(displayedResult.explanations.baseline_prediction).toFixed(2)} / 20
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-slate-500">Largest model contributions; these are associations, not causes.</p>
                    <ul className="mt-5 space-y-4">
                      {featureContributions.map(item => {
                        const magnitude = Math.abs(item.contribution)
                        const width = maxContribution ? Math.max(4, (magnitude / maxContribution) * 100) : 0
                        const featureName = item.feature.replace(/^(num|cat)__/, '').replaceAll('_', ' ')
                        return (
                          <li key={item.feature}>
                            <div className="mb-1 flex items-center justify-between gap-3 text-sm">
                              <span className="capitalize text-slate-700">{featureName}</span>
                              <span className="shrink-0 text-xs text-slate-500">{item.effect}</span>
                            </div>
                            <div className="h-2 overflow-hidden rounded-full bg-slate-100" aria-label={`${featureName} contribution`}>
                              <div
                                className={`h-full rounded-full ${item.contribution >= 0 ? 'bg-blue-600' : 'bg-rose-500'}`}
                                style={{ width: `${width}%` }}
                              />
                            </div>
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                )}

                <button onClick={startPrediction} className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white">
                  New Prediction
                </button>
              </div>
            ) : (
              <div className="rounded-2xl bg-white p-8 text-center">
                <ClipboardList className="mx-auto text-slate-400" size={32} />
                <h3 className="mt-4 font-bold">No prediction available</h3>
                <button onClick={startPrediction} className="mt-4 rounded-xl bg-blue-600 px-5 py-3 text-sm text-white">
                  Predict Grade
                </button>
              </div>
            )
          )}

          {page === 'Recommendations' && (
            <div className="rounded-2xl bg-white p-7">
              <Lightbulb className="text-amber-500" size={28} />
              <h3 className="mt-4 font-bold">Academic Recommendations</h3>
              <p className="mt-2 text-sm text-slate-500">
                Complete a grade prediction to receive personalized recommendations.
              </p>
              <button onClick={startPrediction} className="mt-5 rounded-xl bg-blue-600 px-5 py-3 text-sm text-white">
                Start Prediction
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function Stat({ title, value }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <p className="text-sm text-slate-500">{title}</p>
      <h3 className="mt-3 text-2xl font-bold text-slate-900">{value}</h3>
    </div>
  )
}

export default App
