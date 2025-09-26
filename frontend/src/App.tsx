import { Music, Database, Users, Search } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <Music className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Music Atlas</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="btn-secondary">Login with Spotify</button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Discover Music Through Connections
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform your Spotify listening into a knowledge graph of musical connections. 
            Discover new artists through shared collaborators, geographic origins, and hidden relationships.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Database className="h-12 w-12 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Knowledge Graph</h3>
            <p className="text-gray-600">
              Connect your music data with Wikipedia, MusicBrainz, and concert information 
              to build a comprehensive musical knowledge network.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Users className="h-12 w-12 text-accent-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Smart Recommendations</h3>
            <p className="text-gray-600">
              Get suggestions based on shared collaborators, geographic connections, 
              and musical relationships that traditional algorithms miss.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Search className="h-12 w-12 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Contextual Discovery</h3>
            <p className="text-gray-600">
              Explore music through movies, concerts, and cultural contexts. 
              Find the soundtrack to your interests and experiences.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Explore?</h3>
          <p className="text-gray-600 mb-6">
            Connect your Spotify account to start building your musical knowledge graph.
          </p>
          <button className="btn-primary text-lg px-8 py-3">
            Connect Spotify Account
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2025 Music Atlas. Powered by Neo4j and Spotify.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
