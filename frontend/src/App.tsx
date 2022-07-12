import { ChakraProvider, extendTheme } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AddIndicator } from "./pages/AddIndicator";
import { ExportPage } from "./pages/ExportPage";
import { HomePage } from "./pages/HomePage";
import { ImportPage } from "./pages/ImportPage";
import { PastSubmissions } from "./pages/PastSubmission";
import '@fontsource/noto-sans/400.css'
import '@fontsource/noto-sans/700.css'
import '@fontsource/noto-sans/600.css'
import '@fontsource/noto-sans/500.css'

const theme = extendTheme({
  fonts: {
    body: `'Noto Sans', system-ui, sans-serif`,
    heading: `'Noto Sans', system-ui, sans-serif`,
  }
})

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
