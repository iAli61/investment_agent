import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 py-4 px-6 flex items-center justify-between">
      <div className="flex items-center">
        <h1 className="text-xl font-bold text-blue-600">Property Investment Analysis</h1>
      </div>
      
      <nav className="flex items-center space-x-4">
        <Link to="/dashboard" className="text-gray-600 hover:text-blue-600">Dashboard</Link>
        <Link to="/new-analysis" className="text-gray-600 hover:text-blue-600">New Analysis</Link>
        <Link to="/my-scenarios" className="text-gray-600 hover:text-blue-600">My Scenarios</Link>
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-800">
          <span className="text-sm font-medium">AB</span>
        </div>
      </nav>
    </header>
  );
};

export default Header;