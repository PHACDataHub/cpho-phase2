import { ChakraProvider, extendTheme } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AddIndicator } from "./pages/AddIndicator";
import { ExportPage } from "./pages/ExportPage";
import { HomePage } from "./pages/HomePage";
import { ImportPage } from "./pages/ImportPage";
import { PastSubmissions } from "./pages/PastSubmission";
import "@fontsource/noto-sans/400.css";
import "@fontsource/noto-sans/700.css";
import "@fontsource/noto-sans/600.css";
import "@fontsource/noto-sans/500.css";

const theme = extendTheme({
  fonts: {
    body: `'Noto Sans', system-ui, sans-serif`,
    heading: `'Noto Sans', system-ui, sans-serif`,
  },
  colors: {
    brand: {
      1: "#00bcd4",
      2: "#009688",
      3: "#4caf50",
      4: "#cddc39",
      5: "#ffeb3b",
      6: "#ffc107",
      7: "#ff9800",
      8: "#ff5722",
    },
  },
});

export const App = () => (
  <BrowserRouter>
    <ChakraProvider theme={theme}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/add-indicator" element={<AddIndicator />} />
        <Route path="/past-submissions" element={<PastSubmissions />} />
        <Route path="/export" element={<ExportPage />} />
      </Routes>
    </ChakraProvider>
  </BrowserRouter>
);
