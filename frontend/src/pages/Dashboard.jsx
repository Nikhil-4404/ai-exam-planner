import React, { useEffect, useState } from 'react';
import client from '../api/client';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Calendar, Rocket, Clock, GraduationCap, Grid, List, CheckCircle, AlertCircle } from 'lucide-react';
import SubjectForm from '../components/SubjectForm';

const SummaryCard = ({ title, value, icon: Icon, color }) => (
    <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem' }}>
        <div style={{
            background: color,
            width: '48px', height: '48px',
            borderRadius: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
            <Icon size={24} />
        </div>
        <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>{title}</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, lineHeight: 1.2 }}>{value}</div>
        </div>
    </div>
);

const Dashboard = () => {
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [schedule, setSchedule] = useState(null);
    const [dailyHours, setDailyHours] = useState(4);

    const navigate = useNavigate();
    const userId = localStorage.getItem('user_id');

    useEffect(() => {
        if (!userId) {
            navigate('/');
            return;
        }
        fetchSubjects();
    }, [userId]);

    const fetchSubjects = async () => {
        try {
            const res = await client.get(`/users/${userId}/subjects/`);
            setSubjects(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleAddSubject = async (formData) => {
        const topicList = formData.topics.split(',').map(t => ({
            name: t.trim(),
            weightage: 1.0,
            status: false
        })).filter(t => t.name);

        const payload = {
            name: formData.name,
            exam_date: formData.date,
            difficulty: parseInt(formData.difficulty),
            topics: topicList
        };

        try {
            await client.post(`/users/${userId}/subjects/`, payload);
            fetchSubjects();
            setShowAddForm(false);
        } catch (err) {
            alert("Failed: " + err.message);
        }
    };

    const handleGenerateSchedule = async () => {
        try {
            const res = await client.post(`/schedule/${userId}`, { daily_hours: dailyHours });
            setSchedule(res.data);
        } catch (err) {
            alert("Planning failed: " + err.message);
        }
    };

    // Derived Stats
    const totalSubjects = subjects.length;
    const totalTopics = subjects.reduce((acc, sub) => acc + sub.topics.length, 0);
    const nextExam = subjects.sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))[0];

    return (
        <div className="container animate-enter" style={{ paddingBottom: '4rem' }}>
            {/* Header */}
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingTop: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ background: 'linear-gradient(135deg, #4f46e5, #ec4899)', padding: '0.75rem', borderRadius: '12px' }}>
                        <GraduationCap size={32} color="white" />
                    </div>
                    <div>
                        <h1 style={{ margin: 0, fontSize: '1.75rem' }}>SmartStudy</h1>
                        <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>Welcome back, Student</p>
                    </div>
                </div>
                <button className="btn btn-ghost" onClick={() => { localStorage.removeItem('user_id'); navigate('/'); }}>
                    Log Out
                </button>
            </header>

            {/* Stats Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
                <SummaryCard title="Total Subjects" value={totalSubjects} icon={BookOpen} color="#4f46e5" />
                <SummaryCard title="Total Topics" value={totalTopics} icon={List} color="#ec4899" />
                <SummaryCard title="Next Exam" value={nextExam ? nextExam.name : "No Exams"} icon={Calendar} color="#f59e0b" />
                <SummaryCard title="Study Goal" value={`${dailyHours} hrs/day`} icon={Clock} color="#10b981" />
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading your planner...</div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.2fr', gap: '2rem', alignItems: 'start' }}>

                    {/* Main Content: Subjects List */}
                    <div className="layout-main">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Your Subjects</h2>
                            <button
                                className="btn btn-primary"
                                style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                                onClick={() => setShowAddForm(!showAddForm)}
                            >
                                {showAddForm ? 'Close Form' : '+ Add New Subject'}
                            </button>
                        </div>

                        {showAddForm && (
                            <div className="animate-enter" style={{ marginBottom: '2rem' }}>
                                <SubjectForm onAdd={handleAddSubject} />
                            </div>
                        )}

                        <div style={{ display: 'grid', gap: '1rem' }}>
                            {subjects.length === 0 ? (
                                <div className="card" style={{ textAlign: 'center', padding: '3rem', borderStyle: 'dashed' }}>
                                    <div style={{ marginBottom: '1rem', opacity: 0.5 }}><BookOpen size={48} /></div>
                                    <p>No subjects yet.</p>
                                    <button className="btn btn-ghost" style={{ color: 'var(--primary)' }} onClick={() => setShowAddForm(true)}>Add your first subject</button>
                                </div>
                            ) : (
                                subjects.map(sub => (
                                    <div key={sub.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.75rem', borderRadius: '10px' }}>
                                                <BookOpen size={24} style={{ color: '#818cf8' }} />
                                            </div>
                                            <div>
                                                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{sub.name}</h3>
                                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                                                    {sub.topics.length} Topics • Exam: {sub.exam_date}
                                                </div>
                                            </div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{
                                                fontSize: '0.8rem',
                                                background: sub.difficulty > 7 ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)',
                                                color: sub.difficulty > 7 ? '#fca5a5' : '#6ee7b7',
                                                padding: '4px 10px', borderRadius: '20px', fontWeight: 600, display: 'inline-block'
                                            }}>
                                                Diff: {sub.difficulty}/10
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Sidebar: Planner Generator */}
                    <div className="layout-sidebar" style={{ position: 'sticky', top: '2rem' }}>
                        <div className="card" style={{ background: 'linear-gradient(180deg, rgba(30,41,59,0.8), rgba(15,23,42,0.8))', border: '1px solid rgba(129, 140, 248, 0.2)' }}>
                            <div style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem', marginBottom: '1rem' }}>
                                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <Rocket size={20} color="#f472b6" /> Daily Planner
                                </h3>
                            </div>

                            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                                Our AI analyzes topic weightage and exam proximity to prioritize your day.
                            </p>

                            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                                <label style={{ fontSize: '0.8rem', display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                    Daily Availability
                                </label>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <input
                                        type="number"
                                        value={dailyHours}
                                        onChange={e => setDailyHours(parseFloat(e.target.value))}
                                        step="0.5" min="0.5" max="12"
                                        style={{ margin: 0, width: '80px', textAlign: 'center', fontSize: '1.1rem', fontWeight: 'bold' }}
                                    />
                                    <span style={{ fontSize: '0.9rem' }}>Hours</span>
                                </div>
                            </div>

                            <button onClick={handleGenerateSchedule} className="btn btn-primary" style={{ width: '100%', padding: '1rem', fontSize: '1rem' }}>
                                ✨ Generate Schedule
                            </button>

                            {/* Schedule Output */}
                            {schedule && (
                                <div className="animate-enter" style={{ marginTop: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                        <h4 style={{ margin: 0 }}>Today's Focus</h4>
                                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date().toLocaleDateString()}</span>
                                    </div>

                                    {schedule.length === 0 ? (
                                        <div style={{ textAlign: 'center', padding: '1rem', color: '#10b981', background: 'rgba(16,185,129,0.1)', borderRadius: '8px' }}>
                                            <CheckCircle size={24} style={{ marginBottom: '0.5rem' }} />
                                            <div>You're all caught up!</div>
                                        </div>
                                    ) : (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                            {schedule.map((item, idx) => (
                                                <div key={idx} style={{
                                                    background: 'rgba(255,255,255,0.03)',
                                                    padding: '1rem',
                                                    borderRadius: '10px',
                                                    borderLeft: `4px solid ${item.urgency_score > 1.5 ? '#ef4444' : '#fbbf24'}`,
                                                    transition: 'transform 0.2s',
                                                    cursor: 'default'
                                                }}
                                                    onMouseOver={e => e.currentTarget.style.transform = 'translateX(4px)'}
                                                    onMouseOut={e => e.currentTarget.style.transform = 'translateX(0)'}
                                                >
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                                        <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.5px' }}>{item.subject}</span>
                                                        <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#818cf8' }}>{item.allocated_hours}h</span>
                                                    </div>
                                                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{item.topic}</div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
