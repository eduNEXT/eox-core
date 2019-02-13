import React from 'react';
import { InputText, InputSelect, RadioButtonGroup, RadioButton, TextArea, Button, StatusAlert } from '@edx/paragon'
import { clientRequest } from './client'
import styles from '../css/CourseSettings.css'


export class CourseSettings extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      findCoursesRegex: '',
      openAlert: false,
      statusAlertMessage: '',
      statusAlertType: '',
      courseList: [],
      courseListHtml: [],
      advancedSettingList: [],
      hasAdvancedCourseSettings: false
    }

    this.findCoursesRegexUrl = '/eox-core/management/get_courses';
    this.getAdvancedSettingsListUrl = '/settings/advanced/'

    this.handleChange = this.handleChange.bind(this);
    this.handleFindCoursesSubmit = this.handleFindCoursesSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
  }

  componentDidMount() {
    this.getCourseAdvancedSettings(this.props.courseKey);
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

    this.setState({
      courseListHtml: [],
      openAlert: false
    });

    const searchStringScaped = this.state.findCoursesRegex.replace("+", "%2B");
    const queryUrl = `${this.findCoursesRegexUrl}?search=${searchStringScaped}`;

    clientRequest(
      queryUrl,
      'GET'
    )
    .then(res => res.json())
    .then((response) => {
      if (response.status !== 'Failed')
        this.fillCourseList(response)
      else
        this.failedCourseRegexMatch(response)
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

  fillCourseList(response) {
    let courseList = response.courses.map((courseKey) => {
      return <li key={courseKey}>{courseKey}</li>
    })

    this.setState({
      courseListHtml: courseList
    });
  }

  failedCourseRegexMatch(response) {
    this.setState({
      openAlert: true,
      statusAlertMessage: response.message,
      statusAlertType: 'danger'
    });
  }

  getCourseAdvancedSettings(courseKey) {

    if (courseKey === '') {
      this.setState({
        hasAdvancedCourseSettings: false
      });
      return;
    }

    const queryUrl = `${this.getAdvancedSettingsListUrl}${this.props.courseKey}`
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
        <div className="col-8">
          <label>Current operation will apply to the following courses:</label>
          <div className={styles.coursesList}>
            <ul>{this.state.courseListHtml}</ul>
          </div>
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
            options={this.state.advancedSettingList}
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