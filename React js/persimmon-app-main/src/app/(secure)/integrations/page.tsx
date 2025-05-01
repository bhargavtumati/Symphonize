import { IntegrationCard } from "@/app/components/careers/integration-card"

// This array can be easily extended with new integrations
const integrations = [
  { name: "Career Page", href: "/integrations/career-page" },
  { name: "Zoom Page", href: "/integrations/zoom-integrations" },
  { name: "Brevo Page", href: "/integrations/brevo-integrations" },
  { name: "SendGrid Page", href: "/integrations/sendGrid-integrations" }

  // Add more integrations here as needed
]

export default function IntegrationsPage() {
  return (
    <div className="p-4 w-full">
      <h4 className="text-xl font-semibold mb-6">Integrations</h4>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 sm:gap-4">
        {integrations.map((integration) => (
          <IntegrationCard
            key={integration.name}
            name={integration.name}
            href={integration.href}
          />
        ))}
      </div>
    </div>
  )
}

