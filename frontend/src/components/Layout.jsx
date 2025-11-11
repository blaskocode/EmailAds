/**
 * Main layout component that wraps all pages
 */
import Header from './Header';
import Footer from './Footer';

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <main className="flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
}

export default Layout;

