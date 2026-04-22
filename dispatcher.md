# Dispatcher - Weekly Lead Workflow for Offline Artisans

**Product & Business Artifact**
*AIMS KTT Hackathon - S2.T1.3 - 'Made in Rwanda' Content Recommender*

---

## 1. The Problem

A leatherworker in Nyamirambo has no smartphone, limited internet, and gets most of their information through voice calls and SMS. They cannot browse an online store or check a dashboard. But customers ARE searching for "leather boots" and "cadeau en cuir" online. How do we connect them?

---

## 2. The Weekly Lead Flow

### Who does what?

| Role | Who | What they do |
|------|-----|-------------|
| Aggregator | A cooperative agent with a smartphone (shared among about 10 artisans) | Runs the recommender weekly, collects matched queries |
| Dispatcher | The same agent or a central hub | Sends lead summaries to artisans via SMS or voice |
| Artisan | The maker (no smartphone) | Receives leads, fulfills orders, reports back to agent |

### Step-by-step weekly workflow

```
Day 1 (Monday 8:00 AM)
  |
Agent collects the past week's search queries from the system
  |
Recommender matches queries to local products -> generates "leads"
  |
Agent reviews and groups leads by artisan
  |
Day 1 (Monday 12:00 PM)
  |
Agent sends SMS digest to each artisan (see template below)
  |
Days 2-6
  |
Artisan prepares products / contacts buyer through agent
  |
Day 7 (Sunday)
  |
Agent collects feedback: conversions, sales, issues
  |
Repeat
```

---

## 3. The SMS Digest Template

This is what the artisan receives every Monday:

```
MADE IN RWANDA - Weekly Leads

Hello Jean! This week 8 people searched for your products.

Top leads:
1. "leather boots" - 3 buyers (Kigali)
2. "gift for wife" - 2 buyers (Gasabo)
3. "ceinture en cuir" - 2 buyers (Huye)
4. "wallet men" - 1 buyer (Musanze)

Estimated value: 185,000 RWF
Reply YES to claim a lead
Or call Agent Marie: 0788-123-456
```

### Why these words and numbers?

| Choice | Why |
|--------|-----|
| "Made in Rwanda" | Brand pride - artisans identify with the national label |
| Name greeting | Personal - builds trust and recognition |
| "8 people searched" | Concrete number - shows demand exists |
| Product names in quotes | Clear, no confusion about what is being asked |
| District in parentheses | Tells artisan WHERE the buyer is (helps plan delivery) |
| Estimated value | Motivates action - shows the opportunity in RWF |
| "Reply YES" | Simple one-step action - works on any phone |
| Agent phone number | Backup for those who prefer voice over text |

---

## 4. Key Numbers

| Metric | Value | How we got it |
|--------|-------|--------------|
| Queries per week | About 120 | From our query dataset (120 queries, refreshed weekly) |
| Leads per artisan per week | 5 to 8 | Based on matching 120 queries across 15 artisans |
| Conversions attempted per week | 3 to 5 | Artisans can realistically follow up on about 5 leads per week |
| Sales per week | 2 to 3 | Estimated 50-60% conversion rate on attempted leads |
| Cost per lead (SMS) | About 10 RWF | SMS costs about 7 RWF + aggregator time about 3 RWF |
| Cost per artisan onboarded | About 15,000 RWF | Training + phone setup + first month SMS |
| Average basket size | 25,000 RWF | From catalog data (average price across categories) |
| Weekly revenue per artisan | 50,000 to 75,000 RWF | 2-3 sales times 25,000 RWF |
| Monthly revenue per artisan | 200,000 to 300,000 RWF | About 4 weeks |

---

## 5. 3-Month Pilot Plan (20 Artisans)

### Month 1: Setup and Training

| Activity | Cost |
|----------|------|
| Onboard 20 artisans (training + phone setup) | 300,000 RWF |
| 4 agents with smartphones (shared) | 200,000 RWF |
| SMS costs (20 artisans times 4 weeks) | 8,000 RWF |
| Total Month 1 | 508,000 RWF |

### Month 2: Active Running

| Activity | Cost |
|----------|------|
| SMS + agent time (20 artisans) | 120,000 RWF |
| System hosting (free Colab CPU tier) | 0 RWF |
| Agent stipends (4 agents) | 160,000 RWF |
| Total Month 2 | 280,000 RWF |

### Month 3: Scale and Optimize

| Activity | Cost |
|----------|------|
| Same as Month 2 | 280,000 RWF |
| Add 5 more artisans | 75,000 RWF |
| Total Month 3 | 355,000 RWF |

### Pilot Total: About 1,143,000 RWF (about $440 USD)

### Break-Even Analysis

- Average commission per sale: 2,500 RWF (10% of 25,000 RWF)
- Sales needed to break even: 1,143,000 divided by 2,500 = about 458 sales
- Per artisan over 3 months: 458 divided by 20 = about 23 sales (about 2 sales per week)
- Break-even GMV: about 11,430,000 RWF in total sales

**Conclusion:** If each artisan makes just 2 sales per week, the pilot breaks even in 3 months.

---

## 6. Challenges and Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| Artisan cannot read SMS | Use voice call option or cooperative agent visits |
| Phone battery dies | Agents carry power banks; SMS stores on network for 48 hours |
| Language barrier | Templates in Kinyarwanda, French, and English |
| Buyer does not show up | Require small deposit (1,000 RWF) via mobile money |
| Low query volume | Run ads in local markets to drive searches |

---

## 7. Growth Path

```
Phase 1 (Months 1-3): 20 artisans, manual SMS
Phase 2 (Months 4-6): 50 artisans, automated SMS + voice
Phase 3 (Months 7-12): 200+ artisans, USSD + mobile app
```

---

*Prepared for AIMS KTT Hackathon - S2.T1.3 - Made in Rwanda Content Recommender*
