import { useEffect, useState } from 'react';

function App() {
    const [teams, setTeams] = useState([]);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedTeam1, setSelectedTeam1] = useState('');
    const [selectedTeam2, setSelectedTeam2] = useState('');

    const resolveTeamInfo = (teamCode) => {
        const teamMap = {
            NJN: { code: 'BRK', name: 'Brooklyn Nets'},
            NOH: { code: 'NOP', name: 'New Orleans Pelicans'},
            SEA: { code: 'OKC', name: 'Oklahoma City Thunder'},
            CHA: { code: 'CHA', name: 'Charlotte Hornets'},
            };
            return teamMap[teamCode] || { code: teamCode, name: teamCode};
        }

    console.log("Result object:", result)

    useEffect(() => {
        fetch('https://betai.onrender.com/teams')
        .then(res => res.json())
        .then(setTeams)
        .catch(err => console.error('Failed to fetch teams:', err));
        }, []);

    useEffect(() => {
        //removes old team class
        document.body.classList.forEach(cls => {
            if (cls.startsWith('team-')) {
                document.body.classList.remove(cls);
                }
            });

        // Add predicted winner class
        if (result?.predicted_winner) {
            document.body.classList.add(`team-${result.predicted_winner}`);
            }
        }, [result]);

    const handlePredict = async() => {
        if (!selectedTeam1 || !selectedTeam2) {
            alert("Please select both teams.");
            return;
            }
        if (selectedTeam1 === selectedTeam2) {
            alert("Please select two different teams.");
            return;
            }
        try {
            setLoading(true);
            setResult(null);

            const res = await fetch(`https://betai.onrender.com/predict?team1=${selectedTeam1}&team2=${selectedTeam2}`);
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                } else {
                    setResult(data);
                    setSelectedTeam1('');
                    setSelectedTeam2('');
                }
        } catch (ex) {
                console.error("Prediction Failed: ", ex);
                alert("Something went wrong. Try Again.");
        } finally {
            setLoading(false);
            }
    };
    return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h1>NBA Match-up Predictor</h1>
            {/* Team logos displayed with pulsing glow */}
            {result ? (
                <div style={{
                    position: 'absolute', top: '1rem', right: '1rem', display: 'flex', gap: '0.5rem',
                    alignItems: 'center'
                    }}>
                {/*team 1 logo */}
                <img
                    src={`https://betai.onrender.com/logos/${resolveTeamInfo(result.team1).code}.png`}
                    alt={resolveTeamInfo(result.team1).name}
                    className= {result.predicted_winner === result.team1 ? 'winner-glow' : ''}
                    style={{
                        height: '60px', width: '60px', objectFit: 'contain', borderRadius: '8px',
                        transition: 'box-shadow 0.3s ease'}
                    }}
                />
                {/* team 2 logo */}
                <img
                    src={`https://betai.onrender.com/logos/${resolveTeamInfo(result.team2).code}.png`}
                    alt={resolveTeamInfo(result.team2).name}
                    className= {result.predicted_winner === result.team2 ? 'winner-glow' : ''}
                    style={{
                        height: '60px', width: '60px', objectFit: 'contain', borderRadius: '8px',
                        transition: 'box-shadow 0.3s ease'}
                    }}
                />
            </div>
            ) : (
                <img
                src="https://betai.onrender.com/logos/NBA.png"
                alt='NBA Logo'
                style= {{
                    position: 'absolute', top: '1rem', right: '1rem', height: '60px', width: '60px',
                    objectFit: 'contain'
                    }}
                />
            )}



            <div style={{ marginBottom: '1rem' }}>
                <label>
                    Team 1:
                    <select
                        value={selectedTeam1}
                        onChange={(e) => setSelectedTeam1(e.target.value)}
                        style={{ marginLeft: '0.5rem' }}
                    >
                    <option value="">select</option>
                    {teams.map((team) => (
                        <option key={team} value={team}>{team}</option>
                    ))}
                    </select>
                </label>

                <label style={{ marginLeft: '2rem' }}>
                    Team 2:
                    <select
                        value={selectedTeam2}
                        onChange={(e) => setSelectedTeam2(e.target.value)}
                        style={{ marginLeft: '0.5rem' }}
                    >
                    <option value="">select</option>
                    {teams.map((team) => (
                        <option key={team} value={team}>{team}</option>
                    ))}
                    </select>
                </label>
            </div>

     {/* prediction button */}
    <button onClick={handlePredict}>Predict</button>

    {/* Show while waiting */}
    {loading && <p style={{ marginTop: '1rem' }}>🔄 Predicting...</p>}

    {/* Show result */}
    {result && (
        <div
            className={`team-result team-${result.predicted_winner}`}
            style={{
                marginTop: '2rem',
                padding: '1.5rem',
                borderRadius: '12px',
                transition: 'all 0.4s ease',
            }}
        >
            <h2>
                Predicted Winner: {resolveTeamInfo(result.predicted_winner).name}
                <br />
                ({resolveTeamInfo(result.team1).name}: {result.team1_avg_pts} pts,
                 {resolveTeamInfo(result.team2).name}: {result.team2_avg_pts} pts)
            </h2>
        </div>
    )}
  </div>
);
}
export default App;