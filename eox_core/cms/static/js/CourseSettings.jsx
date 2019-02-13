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
      hasAdvancedCourseSettings: false,
      settingTypeValue: '',
      detailsValue: '',
      advancedValue: ''
    }

    this.findCoursesRegexUrl = '/eox-core/management/get_courses';
    this.getAdvancedSettingsListUrl = '/settings/advanced/'

    this.handleChange = this.handleChange.bind(this);
    this.handleFindCoursesSubmit = this.handleFindCoursesSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.onSubmitSetting = this.onSubmitSetting.bind(this);
  }

  componentDidMount() {
    this.getCourseAdvancedSettings(this.props.courseKey);
  }

  handleChange(value, name) {
    // We need to catch a TypeError error due to some Paragon components returns
    // as parameters the key pair value-name and other components returns
    // the generated event on its onChange event.
    // So, we need to capture both in order to update the state values.
    try {
      const elementValue = value.target.value;
      const elementName = value.target.name;
      this.setState({
        [elementName]: elementValue
      });
    } catch (error) {
      if (error instanceof TypeError) {
        if (value !== name) {
          this.setState({
            [name]: value
          });
        }
      } else {
        throw new Error(error);
      }
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
      courseListHtml: courseList,
      courseList: response.courses
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
      this.setState({
        advancedSettingList: Object.keys(response)
      });
    })
    .catch((error) => {
      console.log(error);
    });
  }

  onSubmitSetting() {
    this.setState({
      openAlert: false
    });

    const isValid = this.onSubmitValidator();
    if (isValid) {
      console.log(this.state.courseList);
    }
  }

  onSubmitValidator() {

    const settingTypeValue = this.state.settingTypeValue;

    if (this.state.courseList.length === 0) {
      this.setState({
        openAlert: true,
        statusAlertMessage: 'No courses selected to apply the changes.',
        statusAlertType: 'danger'
      });
      return false;
    }

    if (settingTypeValue === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: 'Please, select Schedule & details or Advanced settings.',
        statusAlertType: 'danger'
      });
      return false;
    }

    const fieldToCheck = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}Value`);
    const typeMessage = (settingTypeValue === 'details') ? 'Schedule & Details' : 'Advanced settings';
    if (fieldToCheck.value === '') {
      this.setState({
        openAlert: true,
        statusAlertMessage: `Please enter a valid ${typeMessage} value.`,
        statusAlertType: 'danger'
      });
      return false;
    }
    return true;
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
            name="settingTypeValue"
            label="Setting type"
            onChange={this.handleChange}
          >
            <RadioButton value="details">
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
          <TextArea
            name="detailsValue"
            label="New value"
            onChange={this.handleChange}
          />
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
          <TextArea
            name="advancedValue"
            label="New value"
            onChange={this.handleChange}
          />
        </div>
      </div>
      <Button
        label="Apply changes"
        name="apply"
        onClick={this.onSubmitSetting}
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