// DUMMY for now: every function returns made-up data.
// Later each one calls the backend through lib/apiClient.js. The screens will not change.
import { houses, projects, users } from "./dummyData.js";

const wait = (data) =>
  new Promise((resolve) => setTimeout(() => resolve(data), 250));

export const getOverview = () => wait({ houses, projects, users });
