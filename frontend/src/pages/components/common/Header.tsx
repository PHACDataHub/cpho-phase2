import { Heading, HStack, Image, VStack } from "@chakra-ui/react";
import { ColorModeSwitcher } from "../../../ColorModeSwitcher";

export function Header(): JSX.Element {
    return <HStack w="100%" display="flex" justify="space-between" p={5}>
        <Image maxWidth="400px" width="80%" src="logo.svg" />
        {/* TODO: Implement language switcher */}
        {/* <ColorModeSwitcher /> */}
    </HStack>
}