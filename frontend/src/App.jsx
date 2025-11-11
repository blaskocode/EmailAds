import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './contexts/ToastContext';
import UploadPage from './pages/UploadPage';
import PreviewPage from './pages/PreviewPage';
import SuccessPage from './pages/SuccessPage';
import CampaignsListPage from './pages/CampaignsListPage';

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<UploadPage />} />
              <Route path="/campaigns" element={<CampaignsListPage />} />
              <Route path="/preview/:campaignId" element={<PreviewPage />} />
              <Route path="/success/:campaignId" element={<SuccessPage />} />
            </Routes>
          </Layout>
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;

