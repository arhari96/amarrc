import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Balance from './components/Balance';
import BalanceHistory from './components/BalanceHistory';
import './App.css';

const App = () => {
  return (
    <Router>
      <div className="App">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Balance />} />
            <Route path="/history" element={<BalanceHistory />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
