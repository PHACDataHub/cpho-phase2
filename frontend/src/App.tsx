import { ChakraProvider, extendTheme } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AddIndicator } from "./components/pages/AddIndicator";
import { ExportPage } from "./components/pages/ExportPage";
import { HomePage } from "./components/pages/HomePage";
import { ImportPage } from "./components/pages/ImportPage";
import { ModifyPastSubmissions } from "./components/pages/PastSubmission";
import "@fontsource/noto-sans/400.css";
import "@fontsource/noto-sans/700.css";
import "@fontsource/noto-sans/600.css";
import "@fontsource/noto-sans/500.css";
import ModifyIndicator from "./components/pages/ModifyIndicator";

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
  <BrowserRouter basename={process.env.PUBLIC_URL}>
    <ChakraProvider theme={theme}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/add-indicator" element={<AddIndicator />} />
        <Route path="/past-submissions" element={<ModifyPastSubmissions />} />
        <Route path="/export" element={<ExportPage />} />
        <Route path="/modify-indicator/:id" element={<ModifyIndicator />} />
      </Routes>
    </ChakraProvider>
  </BrowserRouter>
);
