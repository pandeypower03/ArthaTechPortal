import { useEffect, useState } from "react";

// Runs a loader (an api.js function) once and returns { data, loading, error }.
// The loader must be a stable function, for example one imported from api.js.
export function useLoad(loader) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    loader()
      .then(
        (data) => !cancelled && setState({ data, loading: false, error: null }),
      )
      .catch(
        (error) =>
          !cancelled && setState({ data: null, loading: false, error }),
      );
    return () => {
      cancelled = true;
    };
  }, [loader]);

  return state;
}
