import {Form, Card, CardBody, Row, Col, Button} from "react-bootstrap";


const CreateContacts = () => {
    return(
    <>
        <h3> Create Contacts</h3>
        <Card>
            <CardBody>
                <Form>
                    <Row className = "mb-3" >
                        <Col md="4">
                            <Form.Group >
                                 <Form.Label>Name</Form.Label>
                                 <Form.Control type="text"></Form.Control>
                            </Form.Group>
                        </Col>
                        <Col md="4">
                            <Form.Group >
                                 <Form.Label>Email</Form.Label>
                                 <Form.Control type="email"></Form.Control>
                            </Form.Group>
                        </Col>
                        <Col md="4">
                              <Form.Group >
                                 <Form.Label>Mobile number</Form.Label>
                                  <Form.Control type="number"></Form.Control>
                              </Form.Group>
                        </Col>
                    </Row>
                    <div>
                        <Button variant="success" className="mx-2">Create </Button>
                        <Button variant="danger">Cancel</Button> 
                    </div>
                </Form>
            </CardBody>
        </Card>
    </>
    )
};

export default CreateContacts;
