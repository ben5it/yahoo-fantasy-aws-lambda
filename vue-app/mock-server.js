import express from "express";
import cookieParser from 'cookie-parser';

const app = express();
const port = 3001;

// Middleware to parse JSON request bodies and cookies
app.use(express.json());
app.use(cookieParser());

// In-memory storage for demonstration purposes

let valid_sessionId = null;

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
  console.log("Request /check_auth: CurrentSessionId", sessionId, "ValidSessionId", valid_sessionId);
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
  console.log("Request /api/leagues: CurrentSessionId", sessionId, "ValidSessionId", valid_sessionId);
  if (sessionId === valid_sessionId) {
    res.json([
      {
        league_key: "454.l.29689",
        league_id: "29689",
        name: "Hupu Alpha 2024-2025",
        logo_url:
          "https://s.yimg.com/ep/cx/blendr/v2/image-y-png_1721252122724.png",
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
        logo_url:
          "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/67c5dbdd01aceece878642155459275a885462bc166ad53f07760f03570f111c.jpg",
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
        logo_url:
          "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/132d3d075691e9503531915c083b69512150bbbdd0ac0cc9c961fa7847f7d2b6.jpg",
        scoring_type: "roto",
        start_date: "2024-10-22",
        end_date: "2025-04-13",
      },
      {
        league_key: "454.l.68157",
        league_id: "68157",
        name: "Never Ending",
        logo_url:
          "https://s.yimg.com/ep/cx/blendr/v2/image-basketball-3-png_1721241401648.png",
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

app.listen(port, () => {
  console.log(`Mock server listening at http://localhost:${port}`);
});
