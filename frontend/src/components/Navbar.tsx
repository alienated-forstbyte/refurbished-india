import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="text-xl font-bold text-primary-600">
            RefurbHub
          </Link>
          <div className="flex gap-6 text-sm font-medium text-gray-600">
            <Link href="/products" className="hover:text-primary-600 transition">
              Products
            </Link>
            <Link href="/deals" className="hover:text-primary-600 transition">
              Deals
            </Link>
            <Link href="/compare" className="hover:text-primary-600 transition">
              Compare
            </Link>
            <Link href="/history" className="hover:text-primary-600 transition">
              History
            </Link>
            <Link href="/alerts" className="hover:text-primary-600 transition">
              Alerts
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
