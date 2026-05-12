"use client";

import { useEffect, useMemo, useState } from "react";

const typewriterPosts = [
  "I rejected a candidate with a perfect resume this week.\n\nHere's why - and what it taught me about what we're actually hiring for when we say \"culture fit.\"\n\nIt's not what you think.",
  "5 years in HR. The #1 mistake companies make is confusing culture fit with culture add. They're not the same thing.",
  "Your job description is why you're not finding the right hire. Here's how we fixed ours - and cut time-to-hire by 40%.",
  "I was invisible on LinkedIn for 6 years. Then I started posting consistently for 47 days. Here's what changed.",
];

const liveFeatures = [
  {
    tag: "Core",
    tagClass: "core",
    title: "Voice Fingerprint Engine",
    desc: "6-minute setup. 47 voice markers extracted from your writing samples. Every post sounds like you, not a chatbot.",
  },
  {
    tag: "Core",
    tagClass: "core",
    title: "AI Chat Agent",
    desc: "Multi-turn refinement with memory. \"Make it shorter.\" \"More contrarian.\" \"Add data.\" It remembers your past posts.",
  },
  {
    tag: "Smart",
    tagClass: "smart",
    title: "Content Calendar",
    desc: "Drag, drop, schedule. Auto-fill empty slots based on your frequency setting. Your whole month visible at a glance.",
  },
  {
    tag: "Core",
    tagClass: "core",
    title: "Banned Phrase Filter",
    desc: "200+ AI red-flag phrases blocked automatically. \"Thrilled to share,\" \"paradigm shift,\" \"let that sink in\" - never make it through.",
  },
];

const nextFeatures = [
  {
    tag: "Coming June",
    title: "LinkedIn API Direct Post",
    desc: "One-click publish to LinkedIn. Waiting on app approval (est. June 15). Currently copy-paste only.",
  },
  {
    tag: "Coming July",
    title: "Analytics Dashboard",
    desc: "Auto-pull impressions via API. Currently self-reported. Chrome extension fallback for Agency tier.",
  },
  {
    tag: "Coming August",
    title: "Agency Multi-Profile",
    desc: "5 client voices, one dashboard. Each with their own fingerprint, library, and calendar. White-label export.",
  },
  {
    tag: "Coming August",
    title: "Chrome Extension",
    desc: "Generate comments while browsing LinkedIn. No tab switching. Comment suggestions on any post in your feed.",
  },
];

const plans = [
  {
    name: "Free",
    price: "0",
    period: "Forever",
    pkr: "PKR 0 / month",
    features: [
      "5 posts per day",
      "10 templates",
      "Voice fingerprint",
      "Gemini Flash AI",
      "Basic analytics",
    ],
    cta: "Start Free",
  },
  {
    name: "Starter",
    price: "9",
    period: "per month",
    pkr: "PKR 999 / month",
    features: [
      "20 posts per day",
      "All 60+ templates",
      "Content calendar",
      "Email reminders",
      "Streak tracking",
    ],
    cta: "Start Trial",
  },
  {
    name: "Pro",
    price: "19",
    period: "per month",
    pkr: "PKR 2,999 / month",
    features: [
      "100 posts per day",
      "Claude AI (Haiku/Sonnet)",
      "Advanced analytics",
      "Carousel builder",
      "Priority support",
      "CSV export",
    ],
    cta: "Start Trial",
    featured: true,
  },
  {
    name: "Agency",
    price: "49",
    period: "per month",
    pkr: "PKR 8,999 / month",
    features: [
      "Unlimited posts",
      "5 client profiles",
      "White-label PDF",
      "Claude Sonnet",
      "API access",
      "Slack support (4h)",
    ],
    cta: "Contact Us",
  },
];

function LogoMark() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <rect width="28" height="28" rx="8" fill="#0D4A45" />
      <path
        d="M8 19.5L13.8 7.5H15.8L21 19.5H18.5L17.4 16.8H12L10.8 19.5H8ZM12.8 14.8H16.6L14.8 10.3L12.8 14.8Z"
        fill="#E8A835"
      />
    </svg>
  );
}

function TinyIcon({ label }: { label: string }) {
  return (
    <svg viewBox="0 0 16 16" aria-label={label} role="img">
      <circle cx="8" cy="8" r="6" fill="currentColor" opacity=".16" />
      <path
        d="M5 8.2l1.8 1.8L11 5.8"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

function HeroMockup() {
  const [postIndex, setPostIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = typewriterPosts[postIndex];
    const timeout = window.setTimeout(
      () => {
        if (!deleting) {
          if (charIndex >= current.length) {
            setDeleting(true);
            return;
          }
          setCharIndex((value) => value + 1);
          return;
        }

        if (charIndex <= 0) {
          setDeleting(false);
          setPostIndex((value) => (value + 1) % typewriterPosts.length);
          return;
        }
        setCharIndex((value) => Math.max(0, value - 4));
      },
      !deleting && charIndex >= current.length ? 2800 : deleting ? 18 : 32,
    );

    return () => window.clearTimeout(timeout);
  }, [charIndex, deleting, postIndex]);

  return (
    <div className="hero-visual" aria-label="Qalam app preview">
      <div className="hero-visual-bg">
        <div className="mock-founder">
          <div className="mock-founder-av">US</div>
          <div>
            <div className="mock-founder-name">Usama&apos;s Qalam</div>
            <div className="mock-founder-role">People & Culture Manager · Lahore</div>
          </div>
        </div>
        <div className="mock-stats">
          <div className="mock-stats-label">This Week</div>
          <div className="mock-stats-num">12 posts</div>
          <div className="mock-stats-change">8 published · 4 scheduled</div>
        </div>

        <div className="product-mock">
          <div className="mock-topbar">
            <div className="mock-dots">
              <div className="mock-dot" />
              <div className="mock-dot" />
              <div className="mock-dot" />
            </div>
            <div className="mock-url">app.qalam.techspirex.com</div>
          </div>
          <div className="mock-body">
            <div className="mock-sidebar">
              <div className="mock-nav-item active"><TinyIcon label="Current post" /> Today&apos;s Post</div>
              <div className="mock-nav-item"><TinyIcon label="Calendar" /> Calendar</div>
              <div className="mock-nav-item"><TinyIcon label="Analytics" /> Analytics</div>
            </div>
            <div className="mock-main">
              <div className="mock-compose">
                <div className="mock-compose-label">Writing in your voice</div>
                <div className="mock-compose-text">
                  {typewriterPosts[postIndex].slice(0, charIndex)}
                  <span className="mock-cursor" />
                </div>
                <div className="mock-meta">
                  <span className="mock-meta-item">Voice match: 94%</span>
                  <span className="mock-meta-item">Banned phrases: 0</span>
                  <span className="mock-meta-item warn">Est. reach: High</span>
                </div>
              </div>
              <div className="mock-chips">
                <div className="mock-chip primary">Today&apos;s Post</div>
                <div className="mock-chip">Contrarian Take</div>
                <div className="mock-chip">Personal Story</div>
                <div className="mock-chip">5 Comments</div>
              </div>
              <div className="mock-post">
                <div className="mock-post-head">
                  <div className="mock-avatar">US</div>
                  <div className="mock-post-meta">
                    <strong>Usama Shahzaib</strong>
                    <span>People & Culture Manager · 2h</span>
                  </div>
                </div>
                <div className="mock-post-text">
                  I rejected a candidate with a perfect resume this week.
                  <br />
                  <br />
                  Here&apos;s why - and what it taught me about what we&apos;re actually hiring for.
                </div>
                <div className="mock-post-stats">
                  <span className="hi">1,322 likes</span>
                  <span className="hi">1,987 comments</span>
                  <span className="hi">36,329 impressions</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ProblemSolution() {
  const [solution, setSolution] = useState(false);

  const content = useMemo(
    () =>
      solution
        ? {
            headline: "with Qalam",
            badge: "The Solution",
            badgeClass: "good",
            title: "Write once in the morning. Be heard all week.",
            desc: "Qalam learns how you write in 6 minutes, then generates posts in your exact voice - your rhythm, your vocabulary, your stories. The result sounds like you on your best day, every day. No more blank screens. No more generic AI slop.",
            avatar: "US",
            name: "Usama Shahzaib",
            role: "People & Culture Manager · 2h",
            post: (
              <>
                I rejected a candidate with a perfect resume this week.
                <br />
                <br />
                Here&apos;s why - and what it taught me about what we&apos;re actually hiring for when we say <strong>&quot;culture fit.&quot;</strong>
                <br />
                <br />
                It&apos;s not what you think.
              </>
            ),
            stats: ["1,322 likes", "1,987 comments", "36,329 impressions"],
          }
        : {
            headline: "on your own",
            badge: "The Problem",
            badgeClass: "bad",
            title: "You post once. Then nothing. The algorithm forgets you exist.",
            desc: "Most professionals know they should be on LinkedIn. Almost none of them are - consistently. Not because they're lazy, but because creating content that sounds like you, every day, is genuinely hard. You stare at a blank screen. You write something generic. You delete it. You tell yourself you'll try tomorrow. Tomorrow never comes.",
            avatar: "",
            name: "Anonymous Professional",
            role: "HR Manager · 4h",
            post: "Excited to share that I am thrilled to announce my new role! Grateful for this opportunity to leverage my skills and foster growth in this dynamic landscape. It's a game-changer! #Blessed #HR #Leadership",
            stats: ["2 likes", "0 comments", "3 impressions"],
          },
    [solution],
  );

  return (
    <section className="prob anim show">
      <div className="prob-inner">
        <div className="prob-header">
          <h2>
            Building a LinkedIn brand
            <br />
            <span>{content.headline}</span>
          </h2>
          <button className="prob-toggle" type="button" onClick={() => setSolution((value) => !value)} aria-pressed={solution}>
            <span className={`toggle-label ${!solution ? "on" : ""}`}>The Problem</span>
            <span className={`toggle-track ${solution ? "on" : ""}`}><span className="toggle-thumb" /></span>
            <span className={`toggle-label ${solution ? "on" : ""}`}>with Qalam</span>
          </button>
        </div>

        <div className="prob-grid">
          <div className="prob-text">
            <span className={`prob-badge ${content.badgeClass}`}>{content.badge}</span>
            <h3>{content.title}</h3>
            <p>{content.desc}</p>
          </div>
          <div className="prob-card">
            <div className="prob-post-head">
              <div className={`prob-post-av ${solution ? "real" : ""}`}>{content.avatar}</div>
              <div className="prob-post-meta">
                <strong>{content.name}</strong>
                <span>{content.role}</span>
              </div>
            </div>
            <div className="prob-post-text">{content.post}</div>
            <div className="prob-post-stats">
              {content.stats.map((stat) => (
                <span className={solution ? "hi" : ""} key={stat}>{stat}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <>
      <nav aria-label="Primary navigation">
        <a href="#" className="nav-logo" aria-label="Qalam home">
          <LogoMark />
          <span className="nav-wordmark">Qalam<span>.</span></span>
        </a>
        <ul className="nav-links">
          <li><a href="#features">Product</a></li>
          <li><a href="#pricing">Pricing</a></li>
          <li><a href="#founder">Founder</a></li>
          <li><a href="#bip">Building in Public</a></li>
        </ul>
        <div className="nav-cta">
          <a href="/login" className="btn-login">Log In</a>
          <a href="#waitlist" className="btn-signup">Join Waitlist</a>
        </div>
      </nav>

      <main>
        <section className="hero">
          <div className="hero-ambient" aria-hidden="true" />
          <div className="hero-badge">
            <span className="hero-badge-label">Building in Public</span>
            <span className="hero-badge-text">Day 47 · 83 waitlist · Lahore, PK · Launching paid June 1</span>
            <span className="hero-badge-arrow">Follow</span>
          </div>

          <h1>
            LinkedIn content that sounds like
            <br />
            <span className="accent">you wrote it</span> - not ChatGPT.
          </h1>
          <p className="hero-sub">
            The AI that learned my voice in 6 minutes, then wrote posts that got me 3 recruiter DMs in 2 weeks.
          </p>
          <div className="hero-chips">
            <span className="hero-chip"><span className="hero-chip-dot green" />47 voice markers extracted from your writing</span>
            <span className="hero-chip"><span className="hero-chip-dot gold" />200+ AI red-flag phrases blocked</span>
            <span className="hero-chip"><span className="hero-chip-dot teal" />Built in Lahore on PKR 1,000/month</span>
          </div>
          <div className="hero-actions">
            <a href="#waitlist" className="btn-hero-main">Join the Waitlist - Free</a>
            <a href="#founder" className="btn-hero-ghost">Read my story</a>
          </div>
          <p className="hero-note">No credit card. No fake urgency. First 100 get 50% off forever as Founding Members.</p>
          <HeroMockup />
        </section>

        <section className="trust-strip" aria-label="Qalam status">
          <div className="trust-inner">
            <div className="trust-left">
              <span className="trust-label">Building in</span>
              <span className="trust-val">Lahore, Pakistan</span>
              <span className="trust-sep">·</span>
              <span className="trust-val gold-text">Day 47 of public build</span>
              <span className="trust-sep">·</span>
              <span className="trust-val">83 waitlist members</span>
            </div>
            <a href="https://linkedin.com/in/usamashahzaib" target="_blank" rel="noreferrer" className="trust-link">Follow on LinkedIn</a>
          </div>
        </section>

        <section className="bip anim show" id="bip">
          <div className="bip-grid">
            <div>
              <div className="bip-eyebrow">Building in Public</div>
              <h2>Every feature is built where you can <em>watch it happen.</em></h2>
              <p>Every feature you see was built yesterday or is being built tomorrow. I post our revenue, our failures, and our wins on LinkedIn using Qalam itself.</p>
              <div className="bip-stats">
                <div><div className="bip-stat-num">Day 47</div><div className="bip-stat-label">Of building publicly</div></div>
                <div><div className="bip-stat-num">$0</div><div className="bip-stat-label">MRR (paid launch June 1)</div></div>
                <div><div className="bip-stat-num">83</div><div className="bip-stat-label">Waitlist members</div></div>
              </div>
              <a href="/building-in-public" className="bip-btn">Read the founder&apos;s journal</a>
            </div>
            <div className="bip-card">
              <div className="bip-card-label">Latest from LinkedIn</div>
              <div className="bip-post">
                &quot;Week 7 of building Qalam: We almost killed the voice fingerprint feature because I thought it was too complex for MVP. Then 3 waitlist members said it was the ONLY reason they signed up. Sometimes the hard thing is the right thing.&quot; <a href="#">#BuildingInPublic</a>
              </div>
              <div className="bip-post-meta">
                <span className="bip-post-date">May 4, 2026 · 2,847 views</span>
                <a href="https://linkedin.com/in/usamashahzaib" target="_blank" rel="noreferrer" className="bip-post-link">View on LinkedIn</a>
              </div>
            </div>
          </div>
        </section>

        <ProblemSolution />

        <section className="feat anim show" id="features">
          <div className="feat-header">
            <div className="feat-eyebrow">Product</div>
            <h2>Not a generic AI writer. A complete LinkedIn growth system.</h2>
            <p className="feat-sub">Qalam learns your voice, blocks AI-sounding phrases, and turns your ideas into a consistent LinkedIn presence.</p>
          </div>
          <div className="feat-grid">
            <div className="feat-col">
              <div className="feat-col-header"><div className="feat-status live" /><span className="feat-col-title">Live Now - May 2026</span></div>
              <div className="feat-items">
                {liveFeatures.map((feature) => (
                  <div className="feat-item" key={feature.title}>
                    <span className={`feat-item-tag ${feature.tagClass}`}>{feature.tag}</span>
                    <div className="feat-item-title">{feature.title}</div>
                    <div className="feat-item-desc">{feature.desc}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="feat-col">
              <div className="feat-col-header"><div className="feat-status next" /><span className="feat-col-title">Next 60 Days</span></div>
              <div className="feat-items">
                {nextFeatures.map((feature) => (
                  <div className="feat-item next" key={feature.title}>
                    <span className="feat-item-tag power">{feature.tag}</span>
                    <div className="feat-item-title">{feature.title}</div>
                    <div className="feat-item-desc">{feature.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="price anim show" id="pricing">
          <div className="price-header">
            <div className="feat-eyebrow">Pricing</div>
            <h2>Built for Pakistan.<br />Priced for the world.</h2>
            <p className="feat-sub">We charge in PKR because that&apos;s where we built this. You pay in your currency. Same product.</p>
            <div className="price-note">
              <span className="price-note-text"><strong>Pre-launch pricing:</strong> These are our planned rates. First 100 users get <strong>50% off forever</strong> as Founding Members. <a href="#waitlist">Join waitlist</a></span>
            </div>
          </div>
          <div className="price-grid">
            {plans.map((plan) => (
              <div className={`price-card ${plan.featured ? "featured" : ""}`} key={plan.name}>
                {plan.featured ? <div className="price-badge">Best for Founders</div> : null}
                <div className="price-plan">{plan.name}</div>
                <div className="price-num"><span className="price-curr">$</span>{plan.price}</div>
                <div className="price-period">{plan.period}</div>
                <div className="price-pkr">{plan.pkr}</div>
                <div className="price-divider" />
                <ul className="price-feats">
                  {plan.features.map((feature) => (
                    <li key={feature}><span className="price-check">✓</span>{feature}</li>
                  ))}
                </ul>
                <a href="#waitlist" className={`price-btn ${plan.featured ? "price-btn-solid" : "price-btn-outline"}`}>{plan.cta}</a>
              </div>
            ))}
          </div>
        </section>

        <section className="found anim show" id="founder">
          <div className="found-inner">
            <div className="found-eyebrow">Founder Story</div>
            <h2>I was invisible on LinkedIn.<br />So I built the tool I <em>needed</em>.</h2>
            <div className="found-body">
              <p>6 years in HR. CPA-HR, CHRMP, TRCP certified. I knew my stuff. But on LinkedIn? I was a ghost. I&apos;d post once a month, get 12 likes, and disappear for 3 weeks.</p>
              <p>I tried ChatGPT. It wrote like a brochure. I tried Jasper. It wrote like a marketer. I needed something that wrote like <em>me</em> - direct, HR-specific, occasionally sarcastic, always honest.</p>
              <p>So I built Qalam in Lahore, on a <strong>PKR 1,000/month budget</strong> (~$3.50 USD), while working full-time as People & Culture Manager. Every feature was built because I needed it first. Every price was set because I know what professionals in Pakistan can actually afford.</p>
              <p>This isn&apos;t Silicon Valley software with Pakistani pricing slapped on. This is <em>built here, for here, by someone who lives here</em>.</p>
            </div>
            <div className="found-profile">
              <div className="found-av">US</div>
              <div className="found-info">
                <div className="found-name">Usama Shahzaib</div>
                <div className="found-role">Founder, Qalam · People & Culture Manager · Lahore, Pakistan</div>
                <a href="https://linkedin.com/in/usamashahzaib" target="_blank" rel="noreferrer" className="found-link">Follow on LinkedIn</a>
              </div>
            </div>
            <a href="/building-in-public" className="found-btn">Read the full build journey</a>
          </div>
        </section>

        <section className="cta anim show" id="waitlist">
          <h2>Your audience is waiting.<br /><em>Start now.</em></h2>
          <p>6 minutes to set up your voice. Join the waitlist today. Be among the first 100 Founding Members - 50% off forever.</p>
          <div className="cta-actions">
            <a href="#waitlist" className="btn-hero-main">Join the Waitlist - Free</a>
            <a href="#pricing" className="btn-hero-ghost">See all plans</a>
          </div>
          <p className="cta-fine">No credit card required · 30-day money back guarantee · Cancel anytime</p>
        </section>
      </main>

      <footer>
        <div className="footer-grid">
          <div>
            <div className="footer-brand">Qalam<span>.</span></div>
            <div className="footer-tagline">The Pen That Never Runs Dry</div>
            <p className="footer-desc">Built in Lahore, Pakistan by a team of one so far. Every line of code, every word of copy, every pricing decision made here.</p>
            <a href="/building-in-public" className="footer-link">See how we&apos;re building this</a>
          </div>
          <div className="footer-col">
            <h5>Product</h5>
            <ul className="footer-links">
              <li><a href="#features">Features</a></li>
              <li><a href="#pricing">Pricing</a></li>
              <li><a href="#">Templates</a></li>
              <li><a href="#">API Access</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h5>Company</h5>
            <ul className="footer-links">
              <li><a href="#founder">Founder Story</a></li>
              <li><a href="#bip">Building in Public</a></li>
              <li><a href="#">Blog</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h5>Legal</h5>
            <ul className="footer-links">
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Refund Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2026 Techspirex. All rights reserved.</span>
          <div className="footer-bottom-links">
            <a href="https://linkedin.com/in/usamashahzaib" target="_blank" rel="noreferrer">LinkedIn</a>
            <a href="#">Twitter/X</a>
            <a href="mailto:hello@qalam.techspirex.com">Email</a>
          </div>
        </div>
      </footer>
    </>
  );
}
