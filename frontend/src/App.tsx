import { ChakraProvider, theme } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AddIndicator } from "./pages/AddIndicator";
import { ExportPage } from "./pages/ExportPage";
import { HomePage } from "./pages/HomePage";
import { ImportPage } from "./pages/ImportPage";
import { PastSubmissions } from "./pages/PastSubmission";

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
