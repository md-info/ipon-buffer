# Ipon Nearby integration

This branch supplies a reusable React feature, a mount/update/unmount SDK, a unified Ipon Buffer demonstration at / and /nearby, and a persistent SQLite demo API. It preserves the existing Ipon Buffer savings recommendation engine. An Android WebView demonstration APK is included separately. No GCash integration, native partner SDK or production authentication is claimed.

## Build and embed

From web: npm run build:nearby. Outputs dist-nearby/ipon-nearby.js plus generated CSS. React 18 and react-dom are peer dependencies supplied by the host. The mount API injects its own styles into a Shadow DOM to isolate presentation. A React host may instead import Nearby and its CSS directly from source.

```tsx
import { mountNearby } from './dist-nearby/ipon-nearby.js';
const instance = mountNearby(document.getElementById('nearby'), {
  brand: 'Your Wallet',
  request: walletCommunityTransport,
  openSavings: () => walletRouter.open('savings'),
  savings: { contribution: 12000, essentials: 176000, daily: 25000, asOf: '2026-09-28' }
});
// All amounts are PHP integer centavos. Supply only user-authorized context.
// Refresh the props after a reviewed expense change:
instance.update(updatedHost);
// When leaving the feature:
instance.unmount();
```

`request<T>(path, method?, body?)` returns decoded JSON or throws an Error. Paths are /nearby, /nearby/{id}/react, and /nearby/{id}; the demo prefixes /api/v1. The host owns server-verified identity, tenant isolation, transport, token refresh and authorization. Never accept a browser-provided member ID as verified identity. The feature cannot debit or credit a wallet: openSavings is navigation only. Recommendation values remain host-owned read-only context.

## API behavior

GET /nearby lists timestamped reports, personal reactions and capped demo points. POST /nearby accepts an exact item, quantity, store, demo area, price_minor, observed_at, conditions and optional JPEG data URL. POST /nearby/{id}/react accepts helpful, confirmed, changed or flagged. DELETE removes an owner's report and associated reactions. Existing privacy deletion removes that user's reports, photos and reactions.

Helpful is appreciation; confirmed is an independent self-attested observation, not verified truth. Confirmations are idempotent per identity. Self-reactions are rejected. Confirmed/changed observations replace one another. Confirmations are blocked after 24 hours; report creation accepts observations within seven days. Each report earns at most 15 non-redeemable points (5 per distinct confirmer). Flagged reports are hidden from other members and stop earning points pending review. The prototype has no moderation adjudication console; owners can delete their reports.

## Native wallet integration

A partner Android team can host the web module inside its approved WebView or adapt the React view. This repository includes a development demo APK, not a partner SDK or AAR. Native identity bridging, origins/navigation restrictions, camera/photo permissions and release signing require the partner's implementation and review. No arbitrary JavaScript wallet bridge or transfer capability is exposed by this module.

## Demonstration versus production

The app starts synthetic sessions at login. Session recreation remains possible and is not fraud-resistant. Neighborhoods are fixed demo areas; no GPS or verified resident data is collected. Images are resized/re-encoded client-side, but backend signature checks are not full malware/content inspection. Production needs decoded image verification, object storage, moderation/appeals, abuse and rate controls, resident/store validation, tenant-specific catalogs, reward funding and anti-collusion controls. Do not connect real users or funds to the demo API.

## Product and commercial hypothesis

Pain: users lack current nearby prices for essentials and spend time discovering them. Community reports and independent confirmations can reduce that information gap; thanks and capped points may encourage useful contributions. The savings engine connects reviewed actual expenses to optional buffer contributions. Price differences and points are never counted as deposited savings.

Proposed buyer: wallet provider. Proposed revenue: integration and recurring licensing. Test incremental retention and merchant usage against moderation/reward costs, alongside essential-spending shortfalls and actual buffer contributions. No validated uplift or wallet partnership exists. Sponsored placements must never buy confirmation status.
