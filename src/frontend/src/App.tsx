import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './views/Dashboard'
import ScenarioLibrary from './views/ScenarioLibrary'
import ScenarioBuilder from './views/ScenarioBuilder'
import SimulationResults from './views/SimulationResults'
import ComparisonView from './views/ComparisonView'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scenarios" element={<ScenarioLibrary />} />
        <Route path="/scenarios/new" element={<ScenarioBuilder />} />
        <Route path="/scenarios/:id/edit" element={<ScenarioBuilder />} />
        <Route path="/simulations/:id" element={<SimulationResults />} />
        <Route path="/comparisons/new" element={<ComparisonView />} />
        <Route path="/comparisons/:id" element={<ComparisonView />} />
      </Routes>
    </Layout>
  )
}

export default App
