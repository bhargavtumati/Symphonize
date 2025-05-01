import {Card, Table, CardBody} from "react-bootstrap";
import { BsFillTrash3Fill } from "react-icons/bs";
import { FaPencilAlt } from "react-icons/fa";


const ContactList = () => {
    return(
    <div>
        <h3> Contacts</h3>
        <Card>
            <CardBody>
               <Table> 
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Mobile No.</th>
                        <th>Actions</th>
                    </tr>

                </thead>
                <tbody>
                    <tr>
                        <td>User 1</td>
                        <td>user1@gmail.com</td>
                        <td>123456780</td>
                        <td>
                            <FaPencilAlt/>
                           < BsFillTrash3Fill/>
                        </td>
                    </tr>
                </tbody>
            </Table>
            </CardBody>
        </Card>
    </div>
    )
};

export default ContactList;
