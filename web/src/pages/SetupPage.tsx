import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";

interface Sku {
  id: string;
  name: string;
  category: string;
  brand: string;
  color: string;
  unit_price: number;
  currency: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  calzado:      "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400",
  bolsos:       "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400",
  electrónica:  "bg-violet-50 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
  accesorios:   "bg-pink-50 text-pink-700 dark:bg-pink-500/10 dark:text-pink-400",
  lifestyle:    "bg-teal-50 text-teal-700 dark:bg-teal-500/10 dark:text-teal-400",
  indumentaria: "bg-orange-50 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400",
};

export default function SetupPage() {
  const baseUrl = window.location.origin.replace("5173", "8000");
  const { apiFetch } = useApi();
  const [reloadStatus, setReloadStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [catalog, setCatalog] = useState<Sku[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/catalog")
      .then((data: Sku[]) => setCatalog(data))
      .catch(console.error)
      .finally(() => setCatalogLoading(false));
  }, [apiFetch]);

  const webhooks = [
    {
      label: "WhatsApp (Twilio)",
      url: `${baseUrl}/webhook/whatsapp`,
      description: "Pegalo en Twilio Sandbox → Messaging → Sandbox Settings → When a message comes in",
    },
    {
      label: "Facebook Messenger (Twilio)",
      url: `${baseUrl}/webhook/messenger`,
      description: "Pegalo en Twilio → Messaging → Senders → Messenger → Messaging Configuration",
    },
  ];

  const envVars = [
    { key: "ANTHROPIC_API_KEY", hint: "console.anthropic.com → API Keys" },
    { key: "TWILIO_ACCOUNT_SID", hint: "console.twilio.com → Account Info" },
    { key: "TWILIO_AUTH_TOKEN", hint: "console.twilio.com → Account Info" },
    { key: "TWILIO_WHATSAPP_FROM", hint: "ej. whatsapp:+14155238886" },
    { key: "TWILIO_MESSENGER_FROM", hint: "ej. messenger:123456789012345 (ID de tu página de Facebook)" },
    { key: "OPERATOR_PASSWORD", hint: "Tu contraseña para el dashboard" },
    { key: "JWT_SECRET", hint: "String largo y aleatorio (openssl rand -hex 32)" },
  ];

  function copy(text: string) {
    navigator.clipboard.writeText(text);
  }

  async function handleReload() {
    setReloadStatus("loading");
    try {
      await apiFetch("/api/catalog/reload", { method: "POST" });
      const fresh = await apiFetch("/api/catalog");
      setCatalog(fresh);
      setReloadStatus("ok");
    } catch {
      setReloadStatus("error");
    }
  }

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Configuración</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          URLs de webhook y variables de entorno para configuración local
        </p>
      </div>

      {/* Webhook URLs */}
      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-6">
        <h3 className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-4">
          URLs de Webhook
        </h3>
        <div className="space-y-4">
          {webhooks.map((wh) => (
            <div key={wh.label}>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{wh.label}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{wh.description}</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 block rounded-lg bg-gray-50 dark:bg-gray-800 px-3 py-2 text-sm text-gray-800 dark:text-gray-200 font-mono border border-gray-200 dark:border-gray-700 overflow-x-auto">
                  {wh.url}
                </code>
                <button
                  onClick={() => copy(wh.url)}
                  className="shrink-0 px-3 py-2 rounded-lg text-xs font-medium bg-brand-50 text-brand-600 hover:bg-brand-100 dark:bg-brand-500/10 dark:text-brand-400 dark:hover:bg-brand-500/20 transition-colors"
                >
                  Copiar
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Catalog */}
      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-800">
          <div>
            <h3 className="text-base font-semibold text-gray-700 dark:text-gray-300">
              Catálogo de Productos
              {catalog.length > 0 && (
                <span className="ml-2 text-xs font-normal text-gray-400 dark:text-gray-500">
                  {catalog.length} SKUs
                </span>
              )}
            </h3>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              Editá{" "}
              <code className="font-mono bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">
                data/catalog.seed.json
              </code>{" "}
              y recargá sin reiniciar el servidor
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {reloadStatus === "ok" && (
              <span className="text-xs text-success-600 dark:text-success-400">Recargado</span>
            )}
            {reloadStatus === "error" && (
              <span className="text-xs text-error-500">Error en el JSON</span>
            )}
            <button
              onClick={handleReload}
              disabled={reloadStatus === "loading"}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-50 transition-colors"
            >
              {reloadStatus === "loading" ? "Recargando…" : "Recargar"}
            </button>
          </div>
        </div>

        {/* SKU table */}
        {catalogLoading ? (
          <div className="py-12 text-center text-sm text-gray-400">Cargando catálogo…</div>
        ) : catalog.length === 0 ? (
          <div className="py-12 text-center text-sm text-gray-400">Sin productos. Verificá catalog.seed.json</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-white/[0.02]">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">Producto</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">Categoría</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">Color</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">Precio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {catalog.map((sku) => (
                  <tr key={sku.id} className="hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                    <td className="px-4 py-3 font-mono text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
                      {sku.id}
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-800 dark:text-white">{sku.name}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500">{sku.brand}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_COLORS[sku.category] ?? "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"}`}>
                        {sku.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 dark:text-gray-400 text-xs capitalize">
                      {sku.color}
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-gray-800 dark:text-white whitespace-nowrap">
                      ${sku.unit_price.toFixed(2)}{" "}
                      <span className="text-xs font-normal text-gray-400">{sku.currency}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Environment variables */}
      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-6">
        <h3 className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-4">
          Variables de Entorno (.env)
        </h3>
        <div className="space-y-3">
          {envVars.map(({ key, hint }) => (
            <div key={key} className="flex items-start gap-3">
              <code className="w-56 shrink-0 rounded-lg bg-gray-50 dark:bg-gray-800 px-3 py-2 text-sm text-gray-800 dark:text-gray-200 font-mono border border-gray-200 dark:border-gray-700">
                {key}
              </code>
              <p className="text-sm text-gray-500 dark:text-gray-400 pt-2">{hint}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick start */}
      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-6">
        <h3 className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Inicio Rápido
        </h3>
        <pre className="rounded-lg bg-gray-50 dark:bg-gray-800 p-4 text-sm font-mono text-gray-700 dark:text-gray-300 overflow-x-auto border border-gray-200 dark:border-gray-700">
{`git clone <repo-url>
cp .env.example .env
# Completar los valores en .env

pip install -r requirements.txt
python scripts/seed.py

uvicorn app.main:app --reload &
cd web && npm install && npm run dev`}
        </pre>
      </div>
    </div>
  );
}
