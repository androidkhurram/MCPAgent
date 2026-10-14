import type { SampleDocument } from './types'

export const SAMPLE_DOCUMENTS: SampleDocument[] = [
  {
    id: 'employee_handbook',
    title: 'Employee Handbook',
    description:
      'Structured policy doc with headings — best for recursive and parent–child chunking.',
    bestStrategies: ['recursive', 'parent-child'],
    suggestedQuestions: [
      'How much is the equipment stipend?',
      'How many remote days are allowed?',
      'When must managers approve schedules?',
    ],
    content: `# Employee Handbook

## Remote Work Policy
Employees may work remotely up to three days per week. Managers must approve schedules by Friday. Equipment stipends are $500 per year. Security training is mandatory before VPN access is granted.

## Leave Policy
Full-time employees receive 20 days of paid leave per year. Leave requests must be submitted at least two weeks in advance. Unused leave rolls over up to five days into the next calendar year.

## Expense Reimbursement
Receipts are required for expenses over $25. Meal reimbursements are capped at $75 per day while traveling. Submit expense reports within 30 days of purchase.`,
  },
  {
    id: 'benefits_policy',
    title: 'Benefits Policy',
    description:
      'Dense paragraph with multiple facts — best for proposition (atomic) chunking.',
    bestStrategies: ['proposition', 'fixed-size'],
    suggestedQuestions: [
      'When does vision coverage start?',
      'What is the dental waiting period?',
      'Are part-time employees eligible for dental?',
    ],
    content: `Acme Health Plan Summary

The Acme Plan covers dental after a six-month waiting period and vision after ninety days for full-time staff. Part-time employees are eligible for vision only after one hundred eighty days. Dental coverage is not available to part-time employees. Emergency room visits require a $150 copay. Prescription drugs are covered with a $10 generic copay.`,
  },
  {
    id: 'company_update',
    title: 'Company Update (mixed topics)',
    description:
      'One article with several topics and no clear headings — compare fixed-size vs recursive.',
    bestStrategies: ['semantic', 'fixed-size', 'recursive'],
    suggestedQuestions: [
      'What is the new Pro price?',
      'When did version 2.0 launch?',
      'How many engineers are we hiring?',
    ],
    content: `Internal Company Update — March 2026

We shipped version 2.0 last week with offline sync and faster search. Customers have been asking for offline mode for over a year, and early feedback has been very positive.

Starting May 1, the Pro plan will be $29 per month instead of $39. Existing customers keep their current price until their contract renews. The Team plan pricing is unchanged at $99 per month.

We are hiring two backend engineers and one designer for the platform team. Applications close on April 15. Referrals receive a $2,000 bonus after the new hire completes 90 days.`,
  },
  {
    id: 'security_faq',
    title: 'Security FAQ (flat text)',
    description:
      'Flat Q&A without headings — good for fixed-size and overlap demos.',
    bestStrategies: ['fixed-size', 'overlap'],
    suggestedQuestions: [
      'What is the VPN requirement?',
      'How often must passwords be rotated?',
      'What happens if I lose my laptop?',
    ],
    content: `Security FAQ

Q: Do I need VPN for remote work?
A: Yes. VPN is required for all remote access to internal systems. Security training must be completed before VPN credentials are issued.

Q: How often should I change my password?
A: Passwords must be rotated every 90 days. Use at least 12 characters with mixed case, numbers, and symbols.

Q: What if I lose my company laptop?
A: Report the loss to IT within one hour. IT will remotely wipe the device and issue a replacement within two business days. You may be liable for unreported losses after 24 hours.`,
  },
]

export function getDocumentById(id: string): SampleDocument | undefined {
  return SAMPLE_DOCUMENTS.find((doc) => doc.id === id)
}
