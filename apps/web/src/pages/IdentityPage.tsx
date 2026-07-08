import { PageHeader } from "../components/PageHeader";

export function IdentityPage() {
  return (
    <>
      <PageHeader
        eyebrow="identity-service"
        title="Identity"
        description="User registration, login, roles, profile security, JWT sessions, and Stripe account mapping."
      />
      <div className="panel">
        <h2>Planned Interfaces</h2>
        <ul>
          <li>Email/password and OAuth login</li>
          <li>Role-based access control</li>
          <li>Stripe customer and subscription status</li>
        </ul>
      </div>
    </>
  );
}
