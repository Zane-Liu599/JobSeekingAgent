import { FaUserEdit } from "react-icons/fa";

import { getStoredUser } from "../api/auth";

export function ProfileSetupPage() {
  const user = getStoredUser();

  return (
    <section className="panel profile-setup-panel">
      <div className="auth-icon-large"><FaUserEdit /></div>
      <p className="eyebrow">Next step</p>
      <h1>Complete your personal information</h1>
      <p className="muted-text">
        {user?.name ? `Welcome, ${user.name}. ` : ""}
        This profile setup area is intentionally empty for now and will be implemented in the next stage.
      </p>
    </section>
  );
}
