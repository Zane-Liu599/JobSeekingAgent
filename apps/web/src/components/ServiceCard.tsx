import { ReactNode } from "react";

type ServiceCardProps = {
  title: string;
  description: string;
  icon: ReactNode;
  action?: string;
};

export function ServiceCard({ title, description, icon, action }: ServiceCardProps) {
  return (
    <article className="service-card">
      <div className="service-icon">{icon}</div>
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
        {action && <span className="card-action">{action}</span>}
      </div>
    </article>
  );
}
