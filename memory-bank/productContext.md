# Product Context: HiBid Email MVP

---

## Problem Statement

Current HiBid email campaign setup process:
- Manual collection of assets from advertisers
- Hours of manual template population
- Multiple back-and-forth communications
- Slow approval cycles (days/weeks)

**Solution:** Automate the entire flow from asset submission to approved email HTML in minutes, not hours.

---

## User Experience Goals

### Primary User Journey

```
1. UPLOAD → User uploads logo, images, text content
   ↓
2. AI PROCESSING → System optimizes content (<5 sec)
   ↓
3. PREVIEW → Desktop + mobile views side-by-side
   ↓
4. APPROVE → Download production-ready HTML
   ✓ Complete in <10 minutes
```

### Key UX Principles

- **Zero Training Required:** Self-explanatory interface
- **Instant Feedback:** Real-time preview updates
- **Mobile-Friendly:** Responsive web interface
- **Error Recovery:** Clear error messages with retry options
- **Progress Indication:** Loading states for all async operations

---

## Core User Flows

### Flow 1: Campaign Creation
1. Navigate to upload page
2. Fill in campaign details (name, advertiser, text)
3. Upload logo (required)
4. Upload 1-3 hero images (optional)
5. Submit form
6. System automatically processes and generates proof
7. Redirect to preview page

### Flow 2: Preview & Approval
1. View desktop and mobile previews
2. Review AI suggestions (subject lines, alt text)
3. Approve or reject campaign
4. If approved: Download HTML file
5. If rejected: Return to upload with pre-filled data

---

## Feature Priorities

### P0: Must-Have (Implemented)
- ✅ Asset upload interface
- ✅ AI processing (text + images)
- ✅ Proof generation (<5 sec)
- ✅ Real-time preview
- ✅ Approval workflow
- ✅ HTML export

### P1: Should-Have (Future)
- Edit & regenerate after preview
- Campaign history view
- Inline text editing

### P2: Nice-to-Have (Post-MVP)
- Multiple template options
- A/B test variations
- Scheduled sending
- Analytics dashboard

---

## Success Metrics

- **Time to Complete:** <10 minutes end-to-end
- **Proof Generation:** 100% under 5 seconds
- **AI Accuracy:** >80% extraction accuracy
- **User Satisfaction:** Self-service completion rate
- **Error Rate:** <5% failed uploads

---

## User Feedback Integration

**Current State:** MVP complete, ready for user testing  
**Future:** Collect feedback on:
- Upload experience
- Preview clarity
- Approval workflow
- HTML output quality

---

## Competitive Context

**Differentiators:**
- Sub-5-second proof generation
- AI-powered content optimization
- Real-time preview
- Production-ready output

**Market Position:** Automated email campaign creation tool for advertisers

