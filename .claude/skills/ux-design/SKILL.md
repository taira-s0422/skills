---
name: ux-design
description: Guides user interface design with accessibility-first methodology, WCAG 2.1 AA compliance, and mobile-first approach
keywords: [design interface, improve UX, user experience, accessibility, responsive design, user flow, UI, WCAG]
---

# UX Design Skill

A user-centered design process enforcing WCAG 2.1 AA accessibility and mobile-first approach.

---

## Non-Negotiable Principles

```
USER NEEDS DRIVE DECISIONS
Never add features without user validation
```

1. **User needs drive decisions** - No features without user validation
2. **Accessibility baseline** - WCAG 2.1 AA minimum, AAA where feasible
3. **Mobile-first design** - Start at 320px viewport
4. **Documented decisions** - Rationale for all design choices
5. **User testing validation** - Test with real users

---

## Mandatory Workflow Phases

### Phase 1: Research
- Define user segments and personas
- Establish success metrics
- Document constraints and requirements
- Identify accessibility needs

### Phase 2: Information Architecture
- Map user flows
- Define content hierarchy
- Design navigation structure
- Create sitemap

### Phase 3: Design Implementation
- Apply WCAG 2.1 AA compliance
- Mobile-first CSS (start at 320px, use min-width queries)
- Implement design tokens
- Create component library

### Phase 4: Validation
- WCAG audit
- Responsive testing
- Performance checks
- User testing

### Phase 5: Documentation
- Component inventory
- Interaction patterns
- Edge cases documentation
- Handoff specifications

---

## Accessibility Standards (WCAG 2.1 AA)

### Core Requirements

| Principle | Requirement |
|-----------|-------------|
| **Perceivable** | Text alternatives, captions, adaptable content |
| **Operable** | Keyboard accessible, enough time, no seizures |
| **Understandable** | Readable, predictable, input assistance |
| **Robust** | Compatible with assistive technologies |

### Specific Metrics

- **Color contrast**: 4.5:1 minimum for normal text, 3:1 for large text
- **Touch targets**: 44×44px minimum (48×48px recommended)
- **Focus indicators**: Visible and clear
- **Alt text**: All meaningful images

---

## Responsive Design

### Mobile-First Approach

```css
/* Start with mobile styles */
.component {
  /* Mobile styles (320px+) */
}

/* Enhance for larger screens */
@media (min-width: 768px) {
  .component {
    /* Tablet styles */
  }
}

@media (min-width: 1024px) {
  .component {
    /* Desktop styles */
  }
}
```

### Breakpoints

| Name | Width | Target |
|------|-------|--------|
| Mobile | 320px+ | Phones |
| Tablet | 768px+ | Tablets |
| Desktop | 1024px+ | Laptops |
| Large | 1440px+ | Desktops |

---

## Design Tokens

### Required Token Categories

- **Colors**: Primary, secondary, semantic (error, success, warning)
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Consistent spacing scale (4px, 8px, 16px, 24px, 32px, etc.)
- **Borders**: Radii, widths
- **Shadows**: Elevation levels
- **Motion**: Duration, easing

---

## Anti-Patterns to Avoid

```
COMBAT GENERIC DESIGN
```

- Avoid predictable patterns without purpose
- No "safe" design choices that lack distinctiveness
- No carousel defaults without user research
- No hamburger menus on desktop without justification
- No infinite scroll without pagination alternative

### Instead

- Distinctive typography choices
- Bold, intentional color palettes
- Meaningful motion and microinteractions
- Data-driven layout decisions

---

## Checklist Before Design

- [ ] User personas defined?
- [ ] Success metrics established?
- [ ] Accessibility requirements documented?
- [ ] Mobile-first approach confirmed?
- [ ] Design tokens prepared?

---

## Checklist Before Handoff

- [ ] WCAG 2.1 AA audit passed?
- [ ] Responsive testing complete (320px to 1440px+)?
- [ ] All touch targets 44×44px+?
- [ ] Color contrast ratios verified?
- [ ] Component documentation complete?
- [ ] Edge cases documented?
- [ ] Developer handoff specs prepared?

---

## Commands

```
/ux-audit         Audit current design for UX issues
/accessibility    Check WCAG compliance
/responsive       Review responsive breakpoints
/user-flow        Map user journey
```

---

## Red Flags - STOP

If you catch yourself:
- Adding features without user validation → STOP, validate first
- Skipping mobile considerations → STOP, mobile-first
- Ignoring accessibility → STOP, WCAG 2.1 AA is baseline
- Making "safe" generic choices → STOP, be intentional
- Designing without defined personas → STOP, research first

---

## Source

Based on [@sebnow/configs/ux-design](https://claude-plugins.dev/skills/@sebnow/configs/ux-design)
