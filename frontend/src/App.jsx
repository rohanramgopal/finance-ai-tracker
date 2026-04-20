import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  BarChart,
  Bar,
} from "recharts";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";
const CHART_COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316", "#14b8a6"];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

function titleCase(text) {
  if (!text) return "N/A";
  return String(text)
    .toLowerCase()
    .split(" ")
    .map((word) => (word ? word[0].toUpperCase() + word.slice(1) : ""))
    .join(" ");
}

export default function App() {
  const [summary, setSummary] = useState({ total_income: 0, total_expense: 0, savings: 0 });
  const [transactions, setTransactions] = useState([]);
  const [insights, setInsights] = useState({ insights: [], health_score: 50 });
  const [budgets, setBudgets] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [dna, setDna] = useState({ persona: "", traits: [], risks: [], recommendations: [] });
  const [subscriptions, setSubscriptions] = useState({ subscriptions: [], monthly_burden: 0, annualized_burden: 0 });
  const [goals, setGoals] = useState([]);
  const [simulation, setSimulation] = useState(null);
  const [whyAnswer, setWhyAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [saveStatus, setSaveStatus] = useState("");

  const [form, setForm] = useState({
    date: new Date().toISOString().slice(0, 10),
    type: "Expense",
    amount: "",
    description: "",
    payment_mode: "UPI",
    category: "",
  });

  const [goalForm, setGoalForm] = useState({
    name: "",
    target_amount: "",
    current_amount: "",
    monthly_contribution: "",
    target_date: "",
  });

  const [simForm, setSimForm] = useState({
    income_change: 0,
    expense_change: 0,
    emi_change: 0,
    rent_change: 0,
    months: 6,
    one_time_cost: 0,
  });

  const safeGet = async (path, fallback) => {
    try {
      const res = await axios.get(`${API_BASE}${path}`);
      return res.data;
    } catch {
      return fallback;
    }
  };

  const loadAll = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        summaryData,
        txData,
        insightsData,
        budgetsData,
        anomaliesData,
        dnaData,
        subsData,
        goalsData,
        whyData,
      ] = await Promise.all([
        safeGet("/summary", { total_income: 0, total_expense: 0, savings: 0 }),
        safeGet("/transactions", []),
        safeGet("/insights", { insights: [], health_score: 50 }),
        safeGet("/budgets", []),
        safeGet("/anomalies", []),
        safeGet("/spending-dna", { persona: "", traits: [], risks: [], recommendations: [] }),
        safeGet("/subscriptions", { subscriptions: [], monthly_burden: 0, annualized_burden: 0 }),
        safeGet("/goals", []),
        safeGet("/why-expense-change", { answer: "" }),
      ]);

      setSummary(summaryData);
      setTransactions(Array.isArray(txData) ? txData : []);
      setInsights(insightsData);
      setBudgets(Array.isArray(budgetsData) ? budgetsData : []);
      setAnomalies(Array.isArray(anomaliesData) ? anomaliesData : []);
      setDna(dnaData);
      setSubscriptions(subsData);
      setGoals(Array.isArray(goalsData) ? goalsData : []);
      setWhyAnswer(whyData?.answer || "");
    } catch {
      setError("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const recentTransactions = useMemo(() => [...transactions].reverse().slice(0, 8), [transactions]);

  const expenseBuckets = useMemo(() => {
    const grouped = {};
    transactions
      .filter((t) => t.type === "Expense")
      .forEach((t) => {
        const category = titleCase(t.category || "Other");
        grouped[category] = (grouped[category] || 0) + Number(t.amount || 0);
      });

    return Object.entries(grouped)
      .map(([category, amount]) => ({ category, amount }))
      .sort((a, b) => b.amount - a.amount);
  }, [transactions]);

  const monthlyTrend = useMemo(() => {
    const grouped = {};
    transactions
      .filter((t) => t.type === "Expense")
      .forEach((t) => {
        const month = String(t.date || "").slice(0, 7);
        grouped[month] = (grouped[month] || 0) + Number(t.amount || 0);
      });

    return Object.entries(grouped)
      .map(([month, amount]) => ({ month, amount }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [transactions]);

  const savingsRate = useMemo(() => {
    if (!summary.total_income) return 0;
    return Math.max(0, Math.round((summary.savings / summary.total_income) * 100));
  }, [summary]);

  const askSuggestion = () => {
    const q = question.toLowerCase().trim();

    if (!q) {
      setAnswer("Type a question first.");
      return;
    }

    if (q.includes("most") || q.includes("highest")) {
      if (!expenseBuckets.length) {
        setAnswer("No expense data available yet.");
        return;
      }
      setAnswer(`You are spending the most on ${expenseBuckets[0].category} (${formatCurrency(expenseBuckets[0].amount)}).`);
      return;
    }

    if (q.includes("save")) {
      if (!expenseBuckets.length) {
        setAnswer("Add some expenses first.");
        return;
      }
      setAnswer(`To save more, review ${expenseBuckets[0].category} first. That is your biggest expense category right now.`);
      return;
    }

    if (q.includes("savings") || q.includes("summary")) {
      setAnswer(`Your total income is ${formatCurrency(summary.total_income)}, total expense is ${formatCurrency(summary.total_expense)}, and savings are ${formatCurrency(summary.savings)}.`);
      return;
    }

    setAnswer("Try asking: Where am I spending the most? How can I save more? What are my savings?");
  };

  const submitTransaction = async (e) => {
    e.preventDefault();
    setSaveStatus("");
    setError("");

    try {
      await axios.post(`${API_BASE}/transactions`, {
        date: form.date,
        type: form.type,
        amount: Number(form.amount),
        description: form.description.trim(),
        payment_mode: form.payment_mode,
        category: form.category.trim(),
      });

      setForm({
        date: new Date().toISOString().slice(0, 10),
        type: "Expense",
        amount: "",
        description: "",
        payment_mode: "UPI",
        category: "",
      });

      setSaveStatus("Transaction added.");
      await loadAll();
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || "Unknown error";
      setError(`Failed to save transaction: ${detail}`);
    }
  };

  const submitGoal = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await axios.post(`${API_BASE}/goals`, {
        name: goalForm.name,
        target_amount: Number(goalForm.target_amount),
        current_amount: Number(goalForm.current_amount || 0),
        monthly_contribution: Number(goalForm.monthly_contribution),
        target_date: goalForm.target_date,
      });

      setGoalForm({
        name: "",
        target_amount: "",
        current_amount: "",
        monthly_contribution: "",
        target_date: "",
      });

      setSaveStatus("Goal added.");
      await loadAll();
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || "Unknown error";
      setError(`Failed to save goal: ${detail}`);
    }
  };

  const runSimulation = async () => {
    setError("");
    try {
      const res = await axios.post(`${API_BASE}/simulate`, {
        income_change: Number(simForm.income_change),
        expense_change: Number(simForm.expense_change),
        emi_change: Number(simForm.emi_change),
        rent_change: Number(simForm.rent_change),
        months: Number(simForm.months),
        one_time_cost: Number(simForm.one_time_cost),
      });
      setSimulation(res.data);
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || "Unknown error";
      setError(`Simulation failed: ${detail}`);
    }
  };

  return (
    <div className="app-shell">
      <div className="ambient ambient-one"></div>
      <div className="ambient ambient-two"></div>

      <div className="container">
        <header className="hero">
          <div className="hero-copy">
            <div className="pill">{getGreeting()}</div>
            <h1>Finance AI Tracker</h1>
            <p className="subtext">
              A clean personal finance dashboard with spending DNA, subscriptions, goals, simulations, and report generation.
            </p>
          </div>
          <div className="hero-actions">
            <button className="secondary-btn" onClick={loadAll}>Refresh</button>
            <a className="secondary-btn link-btn" href={`${API_BASE}/report`} target="_blank" rel="noreferrer">Download CFO Report</a>
          </div>
        </header>

        {error ? <div className="error-box">{error}</div> : null}
        {saveStatus ? <div className="success-box">{saveStatus}</div> : null}

        <section className="stats-grid">
          <div className="metric-card">
            <span className="metric-label">Total Income</span>
            <h2>{formatCurrency(summary.total_income)}</h2>
            <p className="metric-note">All income entries combined</p>
          </div>

          <div className="metric-card">
            <span className="metric-label">Total Expense</span>
            <h2>{formatCurrency(summary.total_expense)}</h2>
            <p className="metric-note">All expense entries combined</p>
          </div>

          <div className="metric-card">
            <span className="metric-label">Savings</span>
            <h2>{formatCurrency(summary.savings)}</h2>
            <p className="metric-note">Income minus expenses</p>
          </div>

          <div className="metric-card">
            <span className="metric-label">Health Score</span>
            <h2>{insights.health_score || 50}/100</h2>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${insights.health_score || 50}%` }}></div>
            </div>
          </div>
        </section>

        <section className="top-grid">
          <div className="panel large-panel">
            <div className="panel-header">
              <div>
                <h3>Add Transaction</h3>
                <p className="panel-subtitle">Quickly record income or expenses.</p>
              </div>
            </div>

            <form className="form-grid" onSubmit={submitTransaction}>
              <div className="field">
                <label>Date</label>
                <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
              </div>

              <div className="field">
                <label>Type</label>
                <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="Expense">Expense</option>
                  <option value="Income">Income</option>
                </select>
              </div>

              <div className="field">
                <label>Amount</label>
                <input type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
              </div>

              <div className="field">
                <label>Description</label>
                <input type="text" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>

              <div className="field">
                <label>Payment Mode</label>
                <select value={form.payment_mode} onChange={(e) => setForm({ ...form, payment_mode: e.target.value })}>
                  <option value="UPI">UPI</option>
                  <option value="Card">Card</option>
                  <option value="Cash">Cash</option>
                  <option value="Bank Transfer">Bank Transfer</option>
                </select>
              </div>

              <div className="field">
                <label>Category</label>
                <input type="text" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
              </div>

              <button className="primary-btn full-width-btn" type="submit">Add Transaction</button>
            </form>
          </div>

          <div className="panel side-panel">
            <div className="panel-header">
              <div>
                <h3>Smart Suggestions</h3>
                <p className="panel-subtitle">Ask simple questions about your finances.</p>
              </div>
            </div>

            <div className="ask-box">
              <input type="text" placeholder="Where am I spending the most?" value={question} onChange={(e) => setQuestion(e.target.value)} />
              <button className="primary-btn" onClick={askSuggestion}>Ask</button>
            </div>

            <div className="answer-box">{answer || "Suggestions will appear here."}</div>

            <div className="mini-cards">
              <div className="mini-card">
                <span>Savings Rate</span>
                <strong>{savingsRate}%</strong>
              </div>
              <div className="mini-card">
                <span>Top Category</span>
                <strong>{expenseBuckets[0]?.category || "N/A"}</strong>
              </div>
            </div>

            <div className="stack-item" style={{ marginTop: "14px" }}>
              <strong>Why did expenses change?</strong>
              <div style={{ marginTop: "8px" }}>{whyAnswer || "No explanation yet."}</div>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Expense Breakdown</h3>
                <p className="panel-subtitle">Category-wise expense distribution.</p>
              </div>
            </div>

            <div className="chart-box">
              {expenseBuckets.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={expenseBuckets} dataKey="amount" nameKey="category" outerRadius={100}>
                      {expenseBuckets.map((entry, index) => (
                        <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="stack-item">No expense data available yet.</div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Monthly Trend</h3>
                <p className="panel-subtitle">Expense trend over time.</p>
              </div>
            </div>

            <div className="chart-box">
              {monthlyTrend.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={monthlyTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="month" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Line type="monotone" dataKey="amount" stroke="#3b82f6" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="stack-item">No trend data available yet.</div>
              )}
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Spending DNA</h3>
                <p className="panel-subtitle">Behavioral spending profile.</p>
              </div>
            </div>

            <div className="stack-item"><strong>Persona:</strong> {dna.persona || "N/A"}</div>

            <div className="stack-list">
              {(dna.traits || []).map((item, index) => <div className="stack-item" key={`trait-${index}`}>{item}</div>)}
              {(dna.risks || []).map((item, index) => <div className="stack-item warning" key={`risk-${index}`}>{item}</div>)}
              {(dna.recommendations || []).map((item, index) => <div className="stack-item" key={`rec-${index}`}>{item}</div>)}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Subscriptions</h3>
                <p className="panel-subtitle">Recurring subscription leakage.</p>
              </div>
            </div>

            <div className="mini-cards">
              <div className="mini-card">
                <span>Monthly Burden</span>
                <strong>{formatCurrency(subscriptions.monthly_burden)}</strong>
              </div>
              <div className="mini-card">
                <span>Annualized Burden</span>
                <strong>{formatCurrency(subscriptions.annualized_burden)}</strong>
              </div>
            </div>

            <div className="stack-list" style={{ marginTop: "14px" }}>
              {(subscriptions.subscriptions || []).length ? (
                subscriptions.subscriptions.map((item, index) => (
                  <div className="stack-item" key={index}>
                    {titleCase(item.merchant)} — {formatCurrency(item.estimated_monthly_cost)}
                  </div>
                ))
              ) : (
                <div className="stack-item">No subscriptions detected.</div>
              )}
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Goal Navigator</h3>
                <p className="panel-subtitle">Track savings goals and projected completion time.</p>
              </div>
            </div>

            <form className="form-grid" onSubmit={submitGoal}>
              <div className="field">
                <label>Goal Name</label>
                <input value={goalForm.name} onChange={(e) => setGoalForm({ ...goalForm, name: e.target.value })} />
              </div>

              <div className="field">
                <label>Target Amount</label>
                <input type="number" value={goalForm.target_amount} onChange={(e) => setGoalForm({ ...goalForm, target_amount: e.target.value })} />
              </div>

              <div className="field">
                <label>Current Amount</label>
                <input type="number" value={goalForm.current_amount} onChange={(e) => setGoalForm({ ...goalForm, current_amount: e.target.value })} />
              </div>

              <div className="field">
                <label>Monthly Contribution</label>
                <input type="number" value={goalForm.monthly_contribution} onChange={(e) => setGoalForm({ ...goalForm, monthly_contribution: e.target.value })} />
              </div>

              <div className="field">
                <label>Target Date</label>
                <input type="date" value={goalForm.target_date} onChange={(e) => setGoalForm({ ...goalForm, target_date: e.target.value })} />
              </div>

              <button className="primary-btn full-width-btn" type="submit">Add Goal</button>
            </form>

            <div className="table-wrap" style={{ marginTop: "18px" }}>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Target</th>
                    <th>Current</th>
                    <th>Months</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {goals.length ? goals.map((goal, index) => (
                    <tr key={index}>
                      <td>{goal.name}</td>
                      <td>{formatCurrency(goal.target_amount)}</td>
                      <td>{formatCurrency(goal.current_amount)}</td>
                      <td>{goal.projected_months}</td>
                      <td>{goal.status}</td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="5">No goals yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Scenario Simulator</h3>
                <p className="panel-subtitle">Run what-if cashflow simulations.</p>
              </div>
            </div>

            <div className="form-grid">
              <div className="field">
                <label>Income Change</label>
                <input type="number" value={simForm.income_change} onChange={(e) => setSimForm({ ...simForm, income_change: e.target.value })} />
              </div>

              <div className="field">
                <label>Expense Change</label>
                <input type="number" value={simForm.expense_change} onChange={(e) => setSimForm({ ...simForm, expense_change: e.target.value })} />
              </div>

              <div className="field">
                <label>EMI Change</label>
                <input type="number" value={simForm.emi_change} onChange={(e) => setSimForm({ ...simForm, emi_change: e.target.value })} />
              </div>

              <div className="field">
                <label>Rent Change</label>
                <input type="number" value={simForm.rent_change} onChange={(e) => setSimForm({ ...simForm, rent_change: e.target.value })} />
              </div>

              <div className="field">
                <label>Months</label>
                <input type="number" value={simForm.months} onChange={(e) => setSimForm({ ...simForm, months: e.target.value })} />
              </div>

              <div className="field">
                <label>One Time Cost</label>
                <input type="number" value={simForm.one_time_cost} onChange={(e) => setSimForm({ ...simForm, one_time_cost: e.target.value })} />
              </div>

              <button className="primary-btn full-width-btn" type="button" onClick={runSimulation}>Run Simulation</button>
            </div>

            {simulation ? (
              <div className="stack-list" style={{ marginTop: "18px" }}>
                <div className="stack-item"><strong>Resilience:</strong> {simulation.resilience}</div>
                <div className="stack-item"><strong>Final Balance:</strong> {formatCurrency(simulation.final_balance)}</div>
                <div className="chart-box">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={simulation.timeline}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="month" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Line type="monotone" dataKey="cumulative_balance" stroke="#22c55e" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : null}
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Auto Insights</h3>
                <p className="panel-subtitle">Generated from your current finance data.</p>
              </div>
            </div>

            <div className="stack-list">
              {insights.insights && insights.insights.length ? (
                insights.insights.map((item, index) => (
                  <div className="stack-item" key={index}>{item}</div>
                ))
              ) : (
                <div className="stack-item">No insights available yet.</div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Budget Overview</h3>
                <p className="panel-subtitle">Compare target budgets with actual spend.</p>
              </div>
            </div>

            <div className="chart-box">
              {budgets.length ? (
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={budgets}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="category" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Bar dataKey="budget" fill="#334155" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="actual" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="stack-item">No budget data.</div>
              )}
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Recent Transactions</h3>
                <p className="panel-subtitle">Latest records from your tracker.</p>
              </div>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTransactions.length ? (
                    recentTransactions.map((tx, index) => (
                      <tr key={index}>
                        <td>{String(tx.date).slice(0, 10)}</td>
                        <td>{tx.type}</td>
                        <td>{titleCase(tx.category)}</td>
                        <td>{formatCurrency(tx.amount)}</td>
                        <td>{tx.description}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5">No transactions yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Anomalies</h3>
                <p className="panel-subtitle">Transactions that stand out from normal spending.</p>
              </div>
            </div>

            <div className="stack-list">
              {anomalies.length ? (
                anomalies.map((item, index) => (
                  <div className="stack-item warning" key={index}>
                    <strong>{titleCase(item.category)}</strong>
                    <div>{item.description}</div>
                    <span>{formatCurrency(item.amount)} • {String(item.date).slice(0, 10)}</span>
                  </div>
                ))
              ) : (
                <div className="stack-item">No unusual transactions detected.</div>
              )}
            </div>
          </div>
        </section>

        {loading ? <div className="loading-float">Refreshing data...</div> : null}
      </div>
    </div>
  );
}
