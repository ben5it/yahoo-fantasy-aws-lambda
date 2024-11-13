import express from "express";
import cookieParser from "cookie-parser";

const app = express();
const port = 3001;

// Middleware to parse JSON request bodies and cookies
app.use(express.json());
app.use(cookieParser());

// In-memory storage for demonstration purposes

let valid_sessionId = null;

let getDataCalled = 0;

// Helper function to generate a random session ID
const generateSessionId = () => Math.random().toString(36).substring(2, 15);

app.get("/login", (req, res) => {
  valid_sessionId = generateSessionId();
  console.log("Request /login: GenareateSessionId", valid_sessionId);
  res.cookie("sessionId", valid_sessionId, { httpOnly: true, secure: true });
  res.redirect("/");
});

app.get("/check_auth", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /check_auth: CurrentSessionId",
    sessionId,
    "ValidSessionId",
    valid_sessionId
  );
  if (sessionId === valid_sessionId) {
    res.json({
      authenticated: true,
      user_info: {
        userId: "EQMHXVGZ65XDJ5G57ZRRBKXUTM",
        email: "husthsz@yahoo.com",
        nickname: "邪",
        profile_image:
          "https://s.yimg.com/ag/images/c58ba041-8d68-4d15-91ac-56dde65c1c9fqV_32sq.jpg",
      },
    });
  } else {
    res.json({ authenticated: false });
  }
});

app.get("/api/leagues", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /api/leagues: CurrentSessionId",
    sessionId,
    "ValidSessionId",
    valid_sessionId
  );
  if (sessionId === valid_sessionId) {
    res.json([
      {
        league_key: "454.l.29689",
        league_id: "29689",
        name: "Hupu Alpha 2024-2025",
        url: "https://basketball.fantasysports.yahoo.com/nba/29689",
        logo_url:
          "https://s.yimg.com/ep/cx/blendr/v2/image-y-png_1721252122724.png",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "head",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
        current_week: 4,
        start_week: "1",
        end_week: "23",
      },
      {
        league_key: "454.l.35674",
        league_id: "35674",
        name: "Star Basketball Association",
        url: "https://basketball.fantasysports.yahoo.com/nba/35674",
        logo_url:
          "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/67c5dbdd01aceece878642155459275a885462bc166ad53f07760f03570f111c.jpg",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "head",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
        current_week: 4,
        start_week: "1",
        end_week: "23",
      },
      {
        league_key: "454.l.38297",
        league_id: "38297",
        name: "HUPU BETA 2024-2025",
        url: "https://basketball.fantasysports.yahoo.com/nba/38297",
        logo_url:
          "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/132d3d075691e9503531915c083b69512150bbbdd0ac0cc9c961fa7847f7d2b6.jpg",
        draft_status: "postdraft",
        num_teams: 18,
        scoring_type: "roto",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
      },
      {
        league_key: "454.l.68157",
        league_id: "68157",
        name: "Never Ending",
        url: "https://basketball.fantasysports.yahoo.com/nba/68157",
        logo_url:
          "https://s.yimg.com/ep/cx/blendr/v2/image-basketball-3-png_1721241401648.png",
        draft_status: "predraft",
        num_teams: 15,
        scoring_type: "head",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
        current_week: 4,
        start_week: "1",
        end_week: "23",
      },
    ]);
  } else {
    res.status(401).json({ error: "Unauthorized" });
  }
});

app.get("/api/getdata", (req, res) => {
  const sessionId = req.cookies.sessionId;
  console.log(
    "Request /getdata: CurrentSessionId",
    sessionId,
    "ValidSessionId",
    valid_sessionId
  );
  if (sessionId === valid_sessionId) {
    getDataCalled++;
    let percentage = (getDataCalled % 4) * 25;

    if (percentage === 0) {

      getDataCalled = 0;

      res.json({
        state: "COMPLETED",
        league_id: 29689,
        week: 3,
        result: {
          result_excel:
            "https://fantasy.laohuang.org/data/2024/29689/3/29689_3_result.xlsx",
          bar_chart_week:
            "https://fantasy.laohuang.org/data/2024/29689/3/roto_bar_wk03.png",
          bar_chart_total:
            "https://fantasy.laohuang.org/data/2024/29689/3/roto_bar_total.png",
          radar_chart_teams: [
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_01.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_02.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_03.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_04.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_05.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_06.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_07.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_08.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_09.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_10.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_11.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_12.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_13.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_14.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_15.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_16.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_17.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_team_18.png",
          ],
          radar_chart_forecast: [
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_01.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_02.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_03.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_04.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_05.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_06.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_07.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_08.png",
            "https://fantasy.laohuang.org/data/2024/29689/3/radar_forecast_09.png",
          ],
        },
      });
    } else {
      res.json({ state: "IN_PROGRESS", percentage: percentage });
    }
  } else {
    res.json({ authenticated: false });
  }
});

app.listen(port, () => {
  console.log(`Mock server listening at http://localhost:${port}`);
});
