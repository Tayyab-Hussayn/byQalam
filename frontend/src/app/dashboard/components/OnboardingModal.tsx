import { onboardingSteps } from "../dashboardConfig";

type OnboardingStep = (typeof onboardingSteps)[number];

export function OnboardingModal({
  step,
  currentStep,
  selectedTags,
  onToggleTag,
  onSkip,
  onNext,
}: {
  step: number;
  currentStep: OnboardingStep;
  selectedTags: string[];
  onToggleTag: (tag: string) => void;
  onSkip: () => void;
  onNext: () => void;
}) {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="progress-bar"><div className="progress-fill" style={{ width: `${currentStep.progress}%` }} /></div>
        <div className="modal-header">
          <div className="modal-step">{currentStep.label}</div>
          <div className="modal-title serif">{currentStep.title}</div>
          <div className="modal-sub">{currentStep.sub}</div>
        </div>
        <div className="modal-body">
          {step === 0 ? <OnboardingIdentity /> : null}
          {step === 1 ? <OnboardingExpertise selectedTags={selectedTags} onToggleTag={onToggleTag} /> : null}
          {step === 2 ? <OnboardingAudience /> : null}
          {step === 3 ? <OnboardingSamples /> : null}
          {step === 4 ? <OnboardingGoals selectedTags={selectedTags} onToggleTag={onToggleTag} /> : null}
          {step === 5 ? <OnboardingComplete /> : null}
        </div>
        <div className="modal-footer">
          <div className="step-dots">
            {onboardingSteps.map((item, index) => (
              <div key={item.label} className={`step-dot ${index < step ? "done" : index === step ? "active" : ""}`} />
            ))}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <button className="modal-skip" type="button" onClick={onSkip}>Skip for now</button>
            <button className="modal-next" type="button" onClick={onNext}>{step === 5 ? "Unleash Qalam ✦" : "Continue →"}</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function OnboardingIdentity() {
  return (
    <>
      <div className="field-row">
        <div className="field-group"><div className="field-label">Full Name</div><input className="field-input" placeholder="e.g. Zara Hussain" /></div>
        <div className="field-group"><div className="field-label">Job Title</div><input className="field-input" placeholder="e.g. Head of Growth" /></div>
      </div>
      <div className="field-group"><div className="field-label">Industry</div><input className="field-input" placeholder="e.g. SaaS / FinTech / Human Resources" /></div>
      <div className="field-group"><div className="field-label">Years of Experience</div><input className="field-input" placeholder="e.g. 8 years" /></div>
    </>
  );
}

function OnboardingExpertise({ selectedTags, onToggleTag }: { selectedTags: string[]; onToggleTag: (tag: string) => void }) {
  const tags = ["Talent Acquisition", "People Strategy", "Leadership", "DEI", "AI in HR", "Culture Building", "Performance Mgmt"];
  return (
    <>
      <div className="field-group">
        <div className="field-label">Expertise Areas (pick 3-5)</div>
        <div className="tag-select">{tags.map((tag) => <button type="button" key={tag} onClick={() => onToggleTag(tag)} className={`tag ${selectedTags.includes(tag) ? "selected" : ""}`}>{tag}</button>)}</div>
      </div>
      <div className="field-group" style={{ marginTop: 16 }}>
        <div className="field-label">Your Unique Perspective</div>
        <textarea className="field-input" rows={3} placeholder="e.g. I believe most performance reviews are broken - and I have data from 200+ exit interviews to prove it." />
        <div style={{ fontSize: 11, color: "var(--text3)", marginTop: 4 }}>This is the most important field. It&apos;s what makes your content unmistakably yours.</div>
      </div>
    </>
  );
}

function OnboardingAudience() {
  return (
    <>
      <div className="field-group"><div className="field-label">Target Audience</div><input className="field-input" placeholder="e.g. HR managers at startups, job seekers in tech, early-stage founders" /></div>
      <div className="field-group" style={{ marginTop: 12 }}><div className="field-label">Their Biggest Struggle</div><textarea className="field-input" rows={2} placeholder="e.g. They don't know how to stand out in a crowded job market without sounding desperate" /></div>
      <div className="field-group" style={{ marginTop: 12 }}><div className="field-label">Their Secret Aspiration</div><textarea className="field-input" rows={2} placeholder="e.g. They want to be the person people turn to for career advice - the LinkedIn voice in their field" /></div>
    </>
  );
}

function OnboardingSamples() {
  return (
    <>
      <div style={{ fontSize: 12, color: "var(--text3)", marginBottom: 12 }}>Paste real posts you&apos;ve written. Qalam will extract your rhythm, vocabulary, and style - this is where the magic happens.</div>
      <div className="sample-box" style={{ marginBottom: 8 }}><textarea rows={5} placeholder={"Your best LinkedIn post - the one that got comments saying 'this is SO you'...\n\nPaste it here exactly as you wrote it."} /></div>
      <div className="sample-box"><textarea rows={4} placeholder="Another post - different topic but same voice. The more variety, the richer the fingerprint..." /></div>
    </>
  );
}

function OnboardingGoals({ selectedTags, onToggleTag }: { selectedTags: string[]; onToggleTag: (tag: string) => void }) {
  const tags = ["Brand Building", "Thought Leadership", "Job Offers", "Client Acquisition", "Network Expansion", "Employer Branding"];
  return (
    <>
      <div className="field-group">
        <div className="field-label">Goals on LinkedIn (select all that apply)</div>
        <div className="tag-select">{tags.map((tag) => <button type="button" key={tag} onClick={() => onToggleTag(tag)} className={`tag ${selectedTags.includes(tag) ? "selected" : ""}`}>{tag}</button>)}</div>
      </div>
      <div className="field-row" style={{ marginTop: 16 }}>
        <div className="field-group"><div className="field-label">Posting Frequency</div><select className="field-input"><option>Daily</option><option>5x / week</option><option>3x / week</option><option>Weekly</option></select></div>
        <div className="field-group"><div className="field-label">Best Post Time</div><select className="field-input"><option>7:00 AM</option><option>9:00 AM</option><option>12:00 PM</option><option>6:00 PM</option></select></div>
      </div>
    </>
  );
}

function OnboardingComplete() {
  return (
    <div style={{ background: "var(--gold-glow)", border: "1px solid var(--border2)", borderRadius: "var(--r12)", padding: 20, textAlign: "center" }}>
      <div style={{ fontSize: 32, marginBottom: 8 }}>🧬</div>
      <div style={{ fontFamily: "var(--font-cormorant),serif", fontSize: 20, color: "var(--gold-light)", marginBottom: 8 }}>Voice Fingerprint Built</div>
      <div style={{ fontSize: 13, color: "var(--text2)", lineHeight: 1.6 }}>Qalam has analyzed your writing and extracted 200+ parameters. Your authenticity score: <strong style={{ color: "var(--gold)" }}>92/100</strong>. Your anti-AI score: <strong style={{ color: "#4CAF50" }}>96/100</strong>.</div>
    </div>
  );
}
