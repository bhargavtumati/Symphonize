import {Navbar, Container} from "react-bootstrap";


const Layout = () => {
    return(
    <div>
        <Navbar>
            <Container>
                <Navbar.Brand>React Tutorial</Navbar.Brand>
                <Navbar.Text>User: Mano</Navbar.Text>
            </Container>
        </Navbar>
    </div>
    )
};

export default Layout;
