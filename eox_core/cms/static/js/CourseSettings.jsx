import React from 'react';
import { InputText, InputSelect, RadioButtonGroup, RadioButton, TextArea, Button, StatusAlert } from '@edx/paragon'
import { clientRequest } from './client'


export class CourseSettings extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      findCoursesRegex: '',
      openAlert: false,
      statusAlertMessage: '',
      statusAlertType: ''
    }

    this.findCoursesRegexUrl = '/eox-core/management/get_courses'

    this.handleChange = this.handleChange.bind(this);
    this.handleFindCoursesSubmit = this.handleFindCoursesSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
  }

  componentDidMount() {

  }

  handleChange(value, name) {
    if (value !== name) {
      this.setState({
        [name]: value
      });
    }
  }

  handleFindCoursesSubmit() {

    if (this.state.findCoursesRegex === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: 'Please, enter a valid course regex.',
        statusAlertType: 'danger'
      });
      return;
    }

    const searchStringScaped = this.state.findCoursesRegex.replace("+", "%2B");
    const queryUrl = `${this.findCoursesRegexUrl}?search=${searchStringScaped}`;

    clientRequest(
      queryUrl,
      'GET'
    )
    .then(res => res.json())
    .then((response) => {
      console.log(response);
    })
    .catch((error) => {
      console.log(error);
    });
  }

  onCloseAlert() {
    this.setState({
      openAlert: false
    });
  }

  render() {
    return (
    <div>
      <div className="row">
        <div className="col-4">
          <InputText
            name="findCoursesRegex"
            label="Enter the course regex"
            onChange={this.handleChange}
            value={this.state.findCoursesRegex}
          />
          <Button
            label="Find courses"
            name="find"
            onClick={this.handleFindCoursesSubmit}
          ></Button>
        </div>
      </div>
      <div className="row">
        <div className="col-4">
          <RadioButtonGroup
            name="type"
            label=""
          >
            <RadioButton value="deatils">
              Schedule & Details
            </RadioButton>
            <RadioButton value="advanced">
              Advanced Settings
            </RadioButton>
          </RadioButtonGroup>
        </div>
        <div className="col-4">
          <InputSelect
            label="Schedule & Details"
            options={this.props.detailsFields}
            name="details"
          />
        </div>
        <div className="col-4">
          <TextArea name="deatils-value" label="New value" value=""/>
        </div>
      </div>
      <div className="row">
        <div className="col-4">

        </div>
        <div className="col-4">
          <InputSelect
            label="Advanced Settings"
            options={this.props.settingsFields}
            name="advanced"
          />
        </div>
        <div className="col-4">
          <TextArea name="advanced-value" label="New value" value=""/>
        </div>
      </div>
      <Button
        label="Apply changes"
        name="apply"
      ></Button>
      <StatusAlert
        dialog={this.state.statusAlertMessage}
        onClose={this.onCloseAlert}
        open={this.state.openAlert}
        alertType={this.state.statusAlertType}
      />
    </div>
    );
  }
}