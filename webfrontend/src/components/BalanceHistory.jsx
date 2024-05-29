import React from 'react';

const BalanceHistory = () => {
  const history = [
    { id: 1, date: '2024-05-01', amount: -100 },
    { id: 2, date: '2024-05-10', amount: 200 },
    { id: 3, date: '2024-05-20', amount: -50 },
  ];

  return (
    <div>
      <h1>Balance History</h1>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          {history.map((entry) => (
            <tr key={entry.id}>
              <td>{entry.date}</td>
              <td>{entry.amount}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BalanceHistory;
