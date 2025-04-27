import { useEffect, useState } from 'react';
import './front_end.css';

function App() {
    const [teams, setTeams] = useState([]);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedTeam1, setSelectedTeam1] = useState('');
    const [selectedTeam2, setSelectedTeam2] = useState('');
    const baseURL = 'https://betai.onrender.com/';

    const resolveTeamInfo = (teamName) => {
        const teamMap = {
          ATL: { code: 'ATL', name: 'Atlanta Hawks' },
          BOS: { code: 'BOS', name: 'Boston Celtics' },
          BRK: { code: 'BRK', name: 'Brooklyn Nets' },
          CHA: { code: 'CHA', name: 'Charlotte Hornets' },
          CHI: { code: 'CHI', name: 'Chicago Bulls' },
          CLE: { code: 'CLE', name: 'Cleveland Cavaliers' },
          DAL: { code: 'DAL', name: 'Dallas Mavericks' },
          DEN: { code: 'DEN', name: 'Denver Nuggets' },
          DET: { code: 'DET', name: 'Detroit Pistons' },
          GSW: { code: 'GSW', name: 'Golden State Warriors' },
          HOU: { code: 'HOU', name: 'Houston Rockets' },
          IND: { code: 'IND', name: 'Indiana Pacers' },
          LAC: { code: 'LAC', name: 'Los Angeles Clippers' },
          LAL: { code: 'LAL', name: 'Los Angeles Lakers' },
          MEM: { code: 'MEM', name: 'Memphis Grizzlies' },
          MIA: { code: 'MIA', name: 'Miami Heat' },
          MIL: { code: 'MIL', name: 'Milwaukee Bucks' },
          MIN: { code: 'MIN', name: 'Minnesota Timberwolves' },
          NOP: { code: 'NOP', name: 'New Orleans Pelicans' },
          NYK: { code: 'NYK', name: 'New York Knicks' },
          OKC: { code: 'OKC', name: 'Oklahoma City Thunder' },
          ORL: { code: 'ORL', name: 'Orlando Magic' },
          PHI: { code: 'PHI', name: 'Philadelphia 76ers' },
          PHX: { code: 'PHX', name: 'Phoenix Suns' },
          POR: { code: 'POR', name: 'Portland Trail Blazers' },
          SAC: { code: 'SAC', name: 'Sacramento Kings' },
          SAS: { code: 'SAS', name: 'San Antonio Spurs' },
          TOR: { code: 'TOR', name: 'Toronto Raptors' },
          UTA: { code: 'UTA', name: 'Utah Jazz' },
          WAS: { code: 'WAS', name: 'Washington Wizards' },
        };
      
        // Try to match by full team name
        const entry = Object.values(teamMap).find(team => team.name === teamName);
      
        if (entry) return entry;
        return { code: teamName, name: teamName }; // fallback
      };

    console.log("Result object:", result)

    useEffect(() => {
        document.body.classList.add('default-sport-theme'); // initially set default theme once
    }, []);

    useEffect(() => {
        fetch(`${baseURL}/teams`)
        .then(res => res.json())
        .then(setTeams)
        .catch(err => console.error('Failed to fetch teams:', err));
        }, []);

        useEffect(() => {
            if (result?.predicted_winner) {
                // Remove previous team themes
                document.body.classList.forEach(cls => {
                    if (cls.startsWith('team-') || cls === 'default-sport-theme') {
                        document.body.classList.remove(cls);
                    }
                });
        
                // Add new team theme
                const winnerCode = resolveTeamInfo(result.predicted_winner).code;
                document.body.classList.add(`team-${winnerCode}`);
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

            const res = await fetch(`${baseURL}/predict?team1=${selectedTeam1}&team2=${selectedTeam2}`);
            console.log(res)
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
                    src={`${baseURL}/logos/${resolveTeamInfo(result.team1).code}.png`}
                    alt={resolveTeamInfo(result.team1).name}
                    className= {result.predicted_winner === result.team1 ? 'winner-glow' : ''}
                    style={{
                        height: '60px', width: '60px', objectFit: 'contain', borderRadius: '8px',
                        transition: 'box-shadow 0.3s ease'
                     }}
                />
                {/* team 2 logo */}
                <img
                    src={`${baseURL}/logos/${resolveTeamInfo(result.team2).code}.png`}
                    alt={resolveTeamInfo(result.team2).name}
                    className= {result.predicted_winner === result.team2 ? 'winner-glow' : ''}
                    style={{
                        height: '60px', width: '60px', objectFit: 'contain', borderRadius: '8px',
                        transition: 'box-shadow 0.3s ease'
                    }}
                />
            </div>
            ) : (
                <img
                src={`${baseURL}/logos/NBA.png`}
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
    {loading && <p style={{ marginTop: '1rem' }}>🔄 Predicting....</p>}

    {/* Show result */}
    {result && (
        <div
            className={`team-result team-${resolveTeamInfo(result.predicted_winner).code}`}
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
                {resolveTeamInfo(result.team1).name}: {result.team1_avg_pts} pts,
                 {resolveTeamInfo(result.team2).name}: {result.team2_avg_pts} pts
            </h2>
        </div>
    )}
  </div>
);
}
export default App;
