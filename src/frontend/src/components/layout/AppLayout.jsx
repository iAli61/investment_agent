import React, { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';

const AppLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div 
        className={`bg-gray-800 text-white transition-all duration-300 ease-in-out ${
          sidebarOpen ? 'w-64' : 'w-16'
        }`}
      >
        <div className="p-4 flex items-center justify-between">
          <h1 className={`font-bold ${sidebarOpen ? 'text-xl' : 'sr-only'}`}>
            InvestCalc
          </h1>
          <button 
            onClick={toggleSidebar}
            className="text-gray-400 hover:text-white focus:outline-none"
          >
            {sidebarOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            )}
          </button>
        </div>

        <nav className="mt-6">
          <div className="px-4 py-2">
            <p className={`text-xs text-gray-400 uppercase font-semibold ${sidebarOpen ? '' : 'sr-only'}`}>
              Analysis Steps
            </p>
            <ul className="mt-2">
              <li className="mb-2">
                <NavLink 
                  to="/property-input" 
                  className={({ isActive }) => `flex items-center p-2 rounded ${
                    isActive ? 'bg-blue-500 text-white' : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  {sidebarOpen && <span className="ml-3">Property Details</span>}
                </NavLink>
              </li>
              <li className="mb-2">
                <NavLink 
                  to="/rental-units" 
                  className={({ isActive }) => `flex items-center p-2 rounded ${
                    isActive ? 'bg-blue-500 text-white' : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  {sidebarOpen && <span className="ml-3">Rental Units</span>}
                </NavLink>
              </li>
              <li className="mb-2">
                <NavLink 
                  to="/financing" 
                  className={({ isActive }) => `flex items-center p-2 rounded ${
                    isActive ? 'bg-blue-500 text-white' : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {sidebarOpen && <span className="ml-3">Financing</span>}
                </NavLink>
              </li>
              <li className="mb-2">
                <NavLink 
                  to="/expenses-tax" 
                  className={({ isActive }) => `flex items-center p-2 rounded ${
                    isActive ? 'bg-blue-500 text-white' : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2zM10 8.5a.5.5 0 11-1 0 .5.5 0 011 0zm5 5a.5.5 0 11-1 0 .5.5 0 011 0z" />
                  </svg>
                  {sidebarOpen && <span className="ml-3">Expenses & Tax</span>}
                </NavLink>
              </li>
              <li className="mb-2">
                <NavLink 
                  to="/analysis-results" 
                  className={({ isActive }) => `flex items-center p-2 rounded ${
                    isActive ? 'bg-blue-500 text-white' : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  {sidebarOpen && <span className="ml-3">Analysis Results</span>}
                </NavLink>
              </li>
            </ul>
          </div>

          {sidebarOpen && (
            <div className="px-4 py-2 mt-8">
              <p className="text-xs text-gray-400 uppercase font-semibold">Tools</p>
              <ul className="mt-2">
                <li className="mb-2">
                  <button className="flex items-center p-2 w-full text-left rounded text-gray-300 hover:bg-gray-700">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                    </svg>
                    <span className="ml-3">Save Scenario</span>
                  </button>
                </li>
                <li className="mb-2">
                  <button className="flex items-center p-2 w-full text-left rounded text-gray-300 hover:bg-gray-700">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    <span className="ml-3">Export PDF</span>
                  </button>
                </li>
              </ul>
            </div>
          )}

          {sidebarOpen && (
            <div className="px-4 py-4 mt-auto absolute bottom-0 w-full">
              <div className="bg-gray-700 rounded-lg p-3 text-sm text-gray-300">
                <p className="font-medium">Need help?</p>
                <p className="mt-1 text-xs">Ask our AI assistant about property investment calculations and strategies.</p>
                <button className="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs w-full">
                  Chat with Assistant
                </button>
              </div>
            </div>
          )}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-x-hidden overflow-y-auto">
        <header className="bg-white shadow">
          <div className="flex items-center justify-between p-4">
            <h1 className="text-xl font-bold text-gray-800">Investment Property Calculator</h1>
            <div className="flex items-center space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                New Analysis
              </button>
            </div>
          </div>
        </header>

        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;