import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import ChatPanel from '../features/ChatPanel';

const Sidebar = () => {
  const location = useLocation();
  const [isChatOpen, setIsChatOpen] = useState(true);
  
  // Navigation items
  const navItems = [
    { path: '/property-input', label: 'Property Details', icon: 'home' },
    { path: '/rental-units', label: 'Rental Units', icon: 'apartment' },
    { path: '/financing', label: 'Financing', icon: 'payments' },
    { path: '/expenses-tax', label: 'Expenses & Tax', icon: 'receipt' },
    { path: '/analysis-results', label: 'Analysis Results', icon: 'insights' },
  ];

  return (
    <div className="w-80 flex flex-col bg-white border-r border-gray-200">
      {/* Navigation Section */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Navigation</h2>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-4 py-3 rounded-lg ${
                location.pathname === item.path
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <span className="material-icons mr-3">{item.icon}</span>
              <span>{item.label}</span>
              {location.pathname === item.path && (
                <span className="ml-auto">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                </span>
              )}
            </Link>
          ))}
        </nav>
      </div>

      {/* Chat Section */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-700">AI Assistant</h2>
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className="text-gray-500 hover:text-blue-600"
          >
            <span className="material-icons">
              {isChatOpen ? 'expand_more' : 'expand_less'}
            </span>
          </button>
        </div>

        {isChatOpen && (
          <div className="flex-1 overflow-hidden">
            <ChatPanel />
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;