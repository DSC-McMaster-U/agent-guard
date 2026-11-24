import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import './ToolCallForm.css'

export interface ToolCallFormValues {
  original_goal: string
  recipient: string
  subject: string
  body: string
}

interface ToolCallFormProps {
  onSubmit: (values: ToolCallFormValues) => void
  busy?: boolean
  error: string | null
}

interface Preset {
  label: string
  recipient: string
  outcome: string
}

// Fictional recipients covering the three demo policy paths. They share one
// harmless message so only the recipient changes the decision.
const PRESETS: Preset[] = [
  { label: 'Internal', recipient: 'teammate@example.com', outcome: 'Expected: allowed' },
  { label: 'Denied', recipient: 'blocked@example.net', outcome: 'Expected: blocked' },
  { label: 'External', recipient: 'partner@example.org', outcome: 'Expected: needs approval' },
]

const PRESET_GOAL = 'Send a short project status update.'
const PRESET_SUBJECT = 'Project status update'
const PRESET_BODY = 'Hi, the demo project is on track for this week. No action is needed.'

const EMPTY_VALUES: ToolCallFormValues = {
  original_goal: '',
  recipient: '',
  subject: '',
  body: '',
}

function ToolCallForm({ onSubmit, busy = false, error }: ToolCallFormProps) {
  const [values, setValues] = useState<ToolCallFormValues>(EMPTY_VALUES)

  function handleChange(event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  function applyPreset(preset: Preset) {
    setValues({
      original_goal: PRESET_GOAL,
      recipient: preset.recipient,
      subject: PRESET_SUBJECT,
      body: PRESET_BODY,
    })
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    // The submit button stays focusable while busy (aria-disabled), so this
    // guard is what blocks duplicate clicks and Enter presses.
    if (busy) return
    onSubmit({
      original_goal: values.original_goal,
      recipient: values.recipient,
      subject: values.subject,
      body: values.body,
    })
  }

  return (
    <section className="tool-call-form" aria-labelledby="tool-call-form-title">
      <h2 id="tool-call-form-title">Try a simulated email</h2>
      <p className="tool-call-form-note">
        This demo evaluates a simulated email. No real mail is sent.
      </p>

      <fieldset className="tool-call-form-presets">
        <legend>Fill with a demo example</legend>
        {PRESETS.map((preset) => (
          <button
            key={preset.recipient}
            type="button"
            aria-label={`${preset.label}: ${preset.recipient}, ${preset.outcome}`}
            disabled={busy}
            onClick={() => applyPreset(preset)}
          >
            <span className="tool-call-form-preset-label">{preset.label}</span>
            <span>{preset.recipient}</span>
            <span>{preset.outcome}</span>
          </button>
        ))}
      </fieldset>

      <form onSubmit={handleSubmit} aria-busy={busy}>
        <div className="tool-call-form-field">
          <label htmlFor="tool-call-recipient">Recipient email</label>
          <input
            id="tool-call-recipient"
            name="recipient"
            type="email"
            autoComplete="off"
            required
            pattern="[^@\s]+@[^@\s]+\.[^@\s]+"
            title="Enter an email address with a domain, such as name@example.com"
            value={values.recipient}
            onChange={handleChange}
          />
        </div>

        <div className="tool-call-form-field">
          <label htmlFor="tool-call-subject">Subject</label>
          <input
            id="tool-call-subject"
            name="subject"
            type="text"
            required
            maxLength={200}
            value={values.subject}
            onChange={handleChange}
          />
        </div>

        <div className="tool-call-form-field">
          <label htmlFor="tool-call-goal">What is the agent trying to do?</label>
          <textarea
            id="tool-call-goal"
            name="original_goal"
            rows={2}
            required
            maxLength={4000}
            value={values.original_goal}
            onChange={handleChange}
          />
        </div>

        <div className="tool-call-form-field">
          <label htmlFor="tool-call-body">Message</label>
          <textarea
            id="tool-call-body"
            name="body"
            rows={6}
            required
            maxLength={10000}
            value={values.body}
            onChange={handleChange}
          />
        </div>

        {error !== null && (
          <p className="tool-call-form-error" role="alert">
            {error}
          </p>
        )}

        <button type="submit" aria-disabled={busy}>
          {busy ? 'Evaluating…' : 'Evaluate email'}
        </button>
      </form>
    </section>
  )
}

export default ToolCallForm
