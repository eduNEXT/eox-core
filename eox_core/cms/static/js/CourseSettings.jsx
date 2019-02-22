import React from 'react';
import {
  InputText, InputSelect, RadioButtonGroup, RadioButton, TextArea, Button, StatusAlert,
} from '@edx/paragon';
import PropTypes from 'prop-types';
import { clientRequest } from './client';
import LoadingIconComponent from './LoadingIcon';
/* eslint-disable import/no-unresolved */
import styles from '../css/CourseSettings';


export default class CourseSettings extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      findCoursesRegex: '',
      openAlert: false,
      statusAlertMessage: '',
      statusAlertType: '',
      courseList: [],
      courseListTextArea: '',
      advancedSettingList: [],
      detailsSettingList: [],
      hasAdvancedCourseSettings: false,
      settingTypeValue: '',
      detailsSettingValue: '',
      advancedSettingValue: '',
      advancedSettingName: '',
      detailsSettingName: '',
      completedTasks: [],
      failedTasks: [],
      isLoading: false,
    };

    this.findCoursesRegexUrl = '/eox-core/management/get_courses';
    this.advancedSettingsUrl = '/settings/advanced/';
    this.detailSettingsUrl = '/settings/details/';

    this.handleChange = this.handleChange.bind(this);
    this.handleFindCoursesSubmit = this.handleFindCoursesSubmit.bind(this);
    this.onCloseAlert = this.onCloseAlert.bind(this);
    this.onSubmitSetting = this.onSubmitSetting.bind(this);
    this.submitNewAdvancedSetting = this.submitNewAdvancedSetting.bind(this);
    this.submitNewDetailSetting = this.submitNewDetailSetting.bind(this);
    this.handleResponse = this.handleResponse.bind(this);
    this.handleCourseListChange = this.handleCourseListChange.bind(this);
  }

  componentDidMount() {
    this.getCourseAdvancedSettings(this.props.courseKey);
    // Adds an empty value at the beginning of the details array.
    if (this.props.detailsFields.length !== 0) {
      this.addEmptyValueToDetailSettings();
    }
  }

  addEmptyValueToDetailSettings() {
    const detailsSettingKeys = this.props.detailsFields;
    detailsSettingKeys.unshift('');
    this.setState({
      detailsSettingList: detailsSettingKeys,
    });
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
        [elementName]: elementValue,
      });
    } catch (error) {
      if (error instanceof TypeError) {
        if (value !== name) {
          this.setState({
            [name]: value,
          });
        }
      } else {
        throw new Error(error);
      }
    }
  }

  handleFindCoursesSubmit(event) {
    event.preventDefault();

    if (this.state.findCoursesRegex === '') {
      this.openStatusAlert('Please, enter a valid course regex.', 'danger');
      return;
    }

    this.setState({
      courseListTextArea: '',
      openAlert: false,
      isLoading: true,
    });

    const searchStringScaped = this.state.findCoursesRegex.replace(/[+*]/gm, '%2B');
    const queryUrl = `${this.findCoursesRegexUrl}?search=${searchStringScaped}`;

    clientRequest(
      queryUrl,
      'GET',
    ).then(
      res => this.handleResponse(res),
    ).then((response) => {
      if (response.status !== 'Failed') {
        this.fillCourseList(response);
      } else {
        this.openStatusAlert(`${response.message}`);
        this.setState({
          isLoading: false,
        });
      }
    }).catch((error) => {
      this.openStatusAlert(`An error occurred in the course regex searching: ${error.message}`, 'danger');
      this.setState({
        isLoading: false,
      });
    });
  }

  onCloseAlert() {
    this.setState({
      openAlert: false,
    });
  }

  fillCourseList(response) {
    const courseList = response.courses.join('\n');
    this.setState({
      courseListTextArea: courseList,
      courseList: response.courses,
      isLoading: false,
    });
  }

  getCourseAdvancedSettings(courseKey) {
    if (courseKey === '') {
      this.openStatusAlert('No course key to obtain course advanced settings.', 'danger');
      return;
    }

    const queryUrl = `${this.advancedSettingsUrl}${this.props.courseKey}`;
    clientRequest(
      queryUrl,
      'GET',
    ).then(
      res => this.handleResponse(res),
    ).then((response) => {
      // Adds an empty value at the beginning of the settings array.
      const advancedSettingKeys = Object.keys(response);
      advancedSettingKeys.unshift('');
      this.setState({
        advancedSettingList: advancedSettingKeys,
      });
    }).catch((error) => {
      this.openStatusAlert(`An error occurred while getting the course advanced settings: ${error.message}`, 'danger');
    });
  }

  onSubmitSetting() {
    this.setState({
      openAlert: false,
    });

    const isValid = this.onSubmitValidator();
    if (isValid) {
      /* eslint-disable no-undef */
      if (!confirm(`Are you sure to change the settings of ${this.state.courseList.length} courses.`)) {
        return;
      }
      const settingTypeValue = this.state.settingTypeValue;
      if (settingTypeValue === 'details') {
        this.submitNewDetailSetting();
      } else if (settingTypeValue === 'advanced') {
        this.submitNewAdvancedSetting();
      }
    }
  }

  onSubmitValidator() {
    const settingTypeValue = this.state.settingTypeValue;

    if (this.state.courseList.length === 0) {
      this.openStatusAlert('No courses selected to apply the changes.', 'danger');
      return false;
    }

    if (settingTypeValue === '') {
      this.openStatusAlert('Please, select Schedule & details or Advanced settings.', 'danger');
      return false;
    }

    const typeSettingName = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}SettingName`);
    const typeMessage = (settingTypeValue === 'details') ? 'Schedule & Details' : 'Advanced settings';

    if (typeSettingName.value === '') {
      this.openStatusAlert(`Please enter a valid ${typeMessage} setting.`, 'danger');
      return false;
    }

    const fieldToCheck = Object.getOwnPropertyDescriptor(this.state, `${settingTypeValue}SettingValue`);
    if (fieldToCheck.value === '') {
      this.openStatusAlert(`Please enter a valid ${typeMessage} value.`, 'danger');
      return false;
    }
    return true;
  }

  submitNewAdvancedSetting() {
    const courses = this.state.courseList;
    const settingName = this.state.advancedSettingName;
    const settingValue = this.state.advancedSettingValue;
    let requestTimeOut = 0;
    this.setState({
      completedTasks: [],
      failedTasks: [],
    });

    const requetsBody = {
      [settingName]: {
        value: this.convertToType(settingValue),
      },
    };

    for (const courseKey of courses) {
      const queryUrl = `${this.advancedSettingsUrl}${courseKey}`;
      setTimeout(() => {
        this.setState({
          isLoading: true,
        });
        clientRequest(
          queryUrl,
          'POST',
          requetsBody,
        ).then(
          res => this.handlePostSettingsResponse(res, courseKey),
        ).catch((error) => {
          console.log(error.message);
          this.setState({
            isLoading: false,
          });
        });
      }, requestTimeOut);
      requestTimeOut += this.props.requestTimeOut;
    }
  }

  submitNewDetailSetting() {
    const courses = this.state.courseList;
    let requestTimeOut = 0;
    this.setState({
      completedTasks: [],
      failedTasks: [],
    });

    for (const courseKey of courses) {
      const queryUrl = `${this.detailSettingsUrl}${courseKey}`;
      // We need to get the current settings in order to updated it.
      setTimeout(() => {
        this.setState({
          isLoading: true,
        });
        clientRequest(
          queryUrl,
          'GET',
        ).then(
          res => this.handleGetDeatilSettingsResponse(res, courseKey),
        ).then((response) => {
          // Deep clone response
          const responseData = JSON.parse(JSON.stringify(response));
          this.postNewDeatilSetting(responseData, queryUrl, courseKey);
        }).catch((error) => {
          console.error(error.message);
          this.setState({
            isLoading: false,
          });
        });
      }, requestTimeOut);
      requestTimeOut += this.props.requestTimeOut;
    }
  }

  handleGetDeatilSettingsResponse(response, courseKey) {
    if (response.ok) {
      return response.json();
    }

    const failedTaskMessage = `An error ocurred while trying to get the settings of ${courseKey}, ${response.statusText}`;
    /* eslint-disable react/no-access-state-in-setstate */
    const actualFailedTasks = this.state.failedTasks;
    actualFailedTasks.push(<li key={courseKey}>{failedTaskMessage}</li>);

    this.setState({
      failedTasks: actualFailedTasks,
      isLoading: false,
    });

    throw new Error(response.statusText);
  }

  postNewDeatilSetting(response, url, courseKey) {
    const settingName = this.state.detailsSettingName;
    const settingValue = this.state.detailsSettingValue;

    response[settingName] = this.convertToType(settingValue);
    this.setState({
      isLoading: true,
    });

    clientRequest(
      url,
      'POST',
      response,
    ).then(
      res => this.handlePostSettingsResponse(res, courseKey),
    ).catch((error) => {
      console.log(error.message);
      this.setState({
        isLoading: false,
      });
    });
  }

  handlePostSettingsResponse(response, courseKey) {
    const successesTaskMessage = `Successful change to ${courseKey}`;
    const actualSuccessTasks = this.state.completedTasks;
    const failedTaskMessage = `An error ocurred while trying to post the settings of ${courseKey}, ${response.statusText}`;
    const actualFailedTasks = this.state.failedTasks;

    if (response.ok) {
      response.json().then(() => {
        actualSuccessTasks.push(<li key={courseKey}>{successesTaskMessage}</li>);
        this.setState({
          completedTasks: actualSuccessTasks,
          isLoading: false,
        });
      }).catch(() => {
        actualFailedTasks.push(<li key={courseKey}>{failedTaskMessage}</li>);
      });
    } else {
      actualFailedTasks.push(<li key={courseKey}>{failedTaskMessage}</li>);
    }

    this.setState({
      failedTasks: actualFailedTasks,
      isLoading: false,
    });
  }

  convertToType(value) {
    try {
      const typeValue = JSON.parse(value);

      if (typeof typeValue === 'boolean') {
        return typeValue;
      }

      if (Array.isArray(typeValue)) {
        return typeValue;
      }

      if (typeof typeValue === 'object') {
        return typeValue;
      }
    } catch (error) {
      if (error instanceof SyntaxError) {
        const dateValue = this.isDateObject(value);
        if (!dateValue) {
          return value;
        }
        return dateValue;
      }
      throw new Error(error);
    }
    const dateValue = this.isDateObject(value);
    if (!dateValue) {
      return value;
    }
    return dateValue;
  }

  /* eslint-disable class-methods-use-this */
  isDateObject(value) {
    const dateLocal = new Date(`${value} UTC`);
    if (dateLocal !== null || dateLocal !== undefined || dateLocal.toString() !== 'Invalid Date') {
      return dateLocal.toJSON();
    }
    return false;
  }

  /* eslint-disable class-methods-use-this */
  handleResponse(response) {
    if (response.ok) {
      return response.json();
    }

    throw new Error(response.statusText);
  }

  openStatusAlert(message, type) {
    this.setState({
      openAlert: true,
      statusAlertMessage: message,
      statusAlertType: type,
    });
  }

  /* eslint-disable no-unused-vars */
  handleCourseListChange(value, name) {
    const courseListRaw = value.split('\n');
    const courseListFiltered = courseListRaw.filter((courseValue) => {
      if (courseValue !== '') {
        return courseValue;
      }
      return false;
    });
    this.setState({
      courseList: courseListFiltered,
    });
  }

  render() {
    return (
      <div>
        <div className="row">
          <div className="col-4">
            <form>
              <InputText
                label="Enter the course regex"
                name="findCoursesRegex"
                onChange={this.handleChange}
                value={this.state.findCoursesRegex}
              />
              <Button
                className={['btn-primary']}
                label="Find courses"
                name="find"
                onClick={this.handleFindCoursesSubmit}
                type="submit"
              />
            </form>
          </div>
          <div className="col-8">
            <TextArea
              className={[styles.coursesList]}
              label="Current operation will apply to the following courses:"
              name="coursesListValue"
              onChange={this.handleCourseListChange}
              value={this.state.courseListTextArea}
            />
          </div>
        </div>
        <div className="row">
          <div className="col-4">
            <RadioButtonGroup
              label="Setting type"
              name="settingTypeValue"
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
              name="detailsSettingName"
              onChange={this.handleChange}
              options={this.state.detailsSettingList}
            />
          </div>
          <div className="col-4">
            <TextArea
              label="New value"
              name="detailsSettingValue"
              onChange={this.handleChange}
            />
          </div>
        </div>
        <div className="row">
          <div className="col-4" />
          <div className="col-4">
            <InputSelect
              label="Advanced Settings"
              name="advancedSettingName"
              onChange={this.handleChange}
              options={this.state.advancedSettingList}
            />
          </div>
          <div className="col-4">
            <TextArea
              label="New value"
              name="advancedSettingValue"
              onChange={this.handleChange}
            />
          </div>
        </div>
        <Button
          className={['btn-primary']}
          label="Apply changes"
          name="apply"
          onClick={this.onSubmitSetting}
        />
        <StatusAlert
          alertType={this.state.statusAlertType}
          dialog={this.state.statusAlertMessage}
          onClose={this.onCloseAlert}
          open={this.state.openAlert}
        />
        <div>
          <h2>Operations complete:</h2>
          <ol>{this.state.completedTasks}</ol>
          <h2>Operations not complete:</h2>
          <ol>{this.state.failedTasks}</ol>
        </div>
        {this.state.isLoading && <LoadingIconComponent />}
      </div>
    );
  }
}

CourseSettings.defaultProps = {
  courseKey: '',
  detailsFields: [],
  requestTimeOut: 500,
};

CourseSettings.propTypes = {
  courseKey: PropTypes.string,
  detailsFields: PropTypes.arrayOf(PropTypes.string),
  requestTimeOut: PropTypes.number,
};
