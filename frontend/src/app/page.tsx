import SearchBar from "@/components/SearchBar";
import StatsCards from "@/components/StatsCards";
import ProductCard from "@/components/ProductCard";
import { getStats, getProducts } from "@/lib/api";

export default async function HomePage() {
  let stats = null;
  let featured = [];
  try {
    stats = await getStats();
    featured = (await getProducts({ sort: "updated", limit: 8 })).products;
  } catch {
    // API may not be available yet
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-12 space-y-12">
      <section className="text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900">
          Refurbished Laptop Search for India
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto">
          Search across Lenovo, Asus, Dell, HP, and more. Track prices, monitor stock, set alerts.
        </p>
        <div className="flex justify-center">
          <SearchBar />
        </div>
      </section>

      <section>
        <StatsCards stats={stats} />
      </section>

      {featured.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold mb-4">Recently Updated</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {featured.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {!stats && (
        <section className="text-center text-gray-400 text-sm">
          Waiting for data... Start the scraper to populate the database.
        </section>
      )}
    </div>
  );
}
