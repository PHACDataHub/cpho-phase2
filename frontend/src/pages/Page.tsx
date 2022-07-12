import { VStack, Heading, Box, Button } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { Footer } from "./components/common/Footer";
import { Header } from "./components/common/Header";

export function Page({
  title,
  subTitle,
  children,
  backButton,
}: {
  title: String;
  subTitle?: String;
  children?: any;
  backButton?: {
    show: boolean;
    redirectUrl: string;
  };
}) {
  let navigate = useNavigate();
  return (
    // <Box textAlign="center">
    //   <VStack backgroundColor={"red.200"} py={10} spacing={8}>
    //     {backButton && backButton.show && (
    //       <Button onClick={() => navigate(backButton.redirectUrl)}>Back</Button>
    //     )}
    //     <Heading fontWeight={700} size="2xl">{title}</Heading>
    //     {subTitle && <Heading fontWeight={700} size="lg">{subTitle}</Heading>}
    //   </VStack>
    //   <>{children}</>
    // </Box>
    <>
    <Header />
    <hr style={{
      marginTop: 10,
      marginBottom: 10,
    }} />
    <Box p={5}>
    {backButton && backButton.show && (<Button onClick={() => navigate(backButton.redirectUrl)}>Back</Button>)}
    <VStack spacing={3} p={5} align="flex-start">
    <Heading fontWeight={700} size="2xl">{title}</Heading>
    {subTitle && <Heading fontWeight={500} size="lg">{subTitle}</Heading>}
    </VStack>
    
    
    {children}
    </Box>
    <Footer />
    </>
  );
}
