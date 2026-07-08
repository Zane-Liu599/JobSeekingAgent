import { PageHeader } from "../components/PageHeader";

export function CommunicationPage() {
  return (
    <>
      <PageHeader
        eyebrow="communication-service"
        title="Communication"
        description="Forum posts, system notifications, user messages, moderation queues, and email delivery workflows."
      />
      <div className="panel">
        <h2>Planned Interfaces</h2>
        <ul>
          <li>Forum categories and threads</li>
          <li>Notification inbox</li>
          <li>Celery-backed async delivery jobs</li>
        </ul>
      </div>
    </>
  );
}
