import { PageHeader } from "../components/PageHeader";

export function PaymentsPage() {
  return (
    <>
      <PageHeader
        eyebrow="Stripe"
        title="Payments"
        description="Subscriptions, checkout, billing portal, customer lifecycle, and entitlement mapping through identity-service."
      />
      <div className="panel">
        <h2>Planned Interfaces</h2>
        <ul>
          <li>Stripe Checkout Session creation</li>
          <li>Billing portal redirects</li>
          <li>Webhook handling and entitlement updates</li>
        </ul>
      </div>
    </>
  );
}
