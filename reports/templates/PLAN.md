# Plan: <title>

- Status: draft | approved | superseded
- Date: YYYY-MM-DD
- Slug: <slug>
- Owner: user / agent
- Approval: awaiting | <quote or link to explicit approval>

## Goal

## Current state and evidence

## In scope

## Out of scope

## Proposed UX and business rules

### Required frontend UX specification

For every frontend change, state before approval:

- affected pages/components and explicitly unchanged areas;
- each user-visible state: default, loading, success, error, empty and
  permission/unauthenticated state where applicable;
- exact user-facing copy or who will approve it;
- navigation, redirect, modal/notification behaviour and user interaction;
- desktop and mobile layout/behaviour.

If any item is intentionally undecided, the plan stays `draft`; implementation
must not invent it.

## Data model, API, Admin and migrations

## Acceptance criteria

## Verification plan

## Risks and rollback

## Open decisions

## Approval record

Do not implement while `Status: draft` or an open decision materially changes
the scope.
