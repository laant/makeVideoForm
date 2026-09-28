// 프로젝트 .env 를 셸 환경변수보다 우선 적용 (예: ~/.zshrc 의 오래된 GEMINI_API_KEY 가 가리지 않게)
import path from "node:path";
import dotenv from "dotenv";
import { ROOT } from "./paths.js";

dotenv.config({ path: path.join(ROOT, ".env"), override: true, quiet: true });
